/** Photo prise ou choisie sur le téléphone, réduite avant l'envoi (décision du 27/11/2026) :
 * 1 280 px de côté au plus, JPEG qualité 0,8 (environ 200 Ko). Le réencodage par le navigateur retire aussi les
 * métadonnées (position GPS, modèle du téléphone) ; le serveur les retire de nouveau par sécurité. */
const MAX_SIDE = 1280;

export async function shrinkPhoto(file: File): Promise<Blob> {
  const bitmap = await loadImage(file);
  const scale = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
  const w = Math.round(bitmap.width * scale);
  const h = Math.round(bitmap.height * scale);
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("canvas");
  ctx.fillStyle = "#fff";   // fond blanc pour les images transparentes
  ctx.fillRect(0, 0, w, h);
  ctx.drawImage(bitmap, 0, 0, w, h);
  for (const quality of [0.8, 0.65, 0.5]) {   // rester sous la limite d'1 Mo du serveur
    const blob = await new Promise<Blob | null>((ok) => canvas.toBlob(ok, "image/jpeg", quality));
    if (blob && blob.size < 950_000) return blob;
  }
  throw new Error("trop lourde");
}

async function loadImage(file: File): Promise<ImageBitmap | HTMLImageElement> {
  if ("createImageBitmap" in window) {
    try {
      // Orientation EXIF appliquée : une photo prise en portrait reste en portrait
      return await createImageBitmap(file, { imageOrientation: "from-image" });
    } catch { /* format que createImageBitmap ne lit pas : repli sur <img> */ }
  }
  const url = URL.createObjectURL(file);
  try {
    const img = new Image();
    img.src = url;
    await img.decode();
    return img;
  } finally {
    URL.revokeObjectURL(url);
  }
}

/** Envoie une photo réduite à une adresse de l'API (champ « file »). */
export function photoForm(blob: Blob): FormData {
  const fd = new FormData();
  fd.append("file", blob, "photo.jpg");
  return fd;
}

/** « il y a 3 jours » pour une date ISO. */
export function daysAgo(iso: string | null | undefined): number | null {
  if (!iso) return null;
  return Math.max(0, Math.floor((Date.now() - Date.parse(iso)) / 86_400_000));
}
