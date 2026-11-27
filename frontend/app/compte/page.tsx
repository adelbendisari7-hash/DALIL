"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";
import VehiclePicker from "@/components/VehiclePicker";
import { api, ApiError, session, type User, type UserCar, type Vehicle } from "@/lib/api";
import { t } from "@/lib/i18n";

type Commune = { id: number; nom_fr: string };
type HistoryItem = {
  session_id: number; created_at: string; text: string; user_vehicle_id: number | null; status: string | null;
  top: { name: string; part: string } | null;
};
type Saved = { token: string; user: User };

const errText = (e: unknown) => (e instanceof ApiError && e.message ? e.message : t("common.error"));

/** Prénom et nom obligatoires ; e-mail, commune, date de naissance et langue facultatifs. */
function ProfileForm({ user, onSaved }: { user: User; onSaved: (u: User) => void }) {
  const [f, setF] = useState({
    first_name: user.first_name ?? "", last_name: user.last_name ?? "", email: user.email ?? "",
    commune_id: user.commune_id ? String(user.commune_id) : "", birth_date: user.birth_date ?? "", lang: user.lang ?? "fr",
  });
  const [communes, setCommunes] = useState<Commune[]>([]);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => { api<Commune[]>("/geo/communes").then(setCommunes).catch(() => undefined); }, []);
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setF({ ...f, [k]: e.target.value });

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    const clear = (["email", "commune_id", "birth_date"] as const).filter((k) => !f[k]);
    try {
      const r = await api<Saved>("/auth/me", {
        method: "PATCH",
        json: {
          first_name: f.first_name, last_name: f.last_name, lang: f.lang, clear,
          email: f.email || null, commune_id: f.commune_id ? Number(f.commune_id) : null, birth_date: f.birth_date || null,
        },
      });
      session.save(r.token, r.user);
      setMsg({ ok: true, text: t("account.saved") });
      onSaved(r.user);
    } catch (err) {
      setMsg({ ok: false, text: errText(err) });
    }
    setBusy(false);
  }

  const opt = <span className="meta"> ({t("account.optional")})</span>;
  return (
    <form onSubmit={save} noValidate>
      <div className="row">
        <div>
          <label htmlFor="first_name">{t("account.firstName")}</label>
          <input id="first_name" autoComplete="given-name" required maxLength={60} value={f.first_name} onChange={set("first_name")} />
        </div>
        <div>
          <label htmlFor="last_name">{t("account.lastName")}</label>
          <input id="last_name" autoComplete="family-name" required maxLength={60} value={f.last_name} onChange={set("last_name")} />
        </div>
      </div>
      <p className="help">{t("account.phone")} : <strong>{user.phone}</strong> ({t("account.phone.verified")})</p>
      <label htmlFor="email">{t("account.email")}{opt}</label>
      <input id="email" type="email" inputMode="email" autoComplete="email" maxLength={160} value={f.email} onChange={set("email")} />
      <label htmlFor="commune">{t("account.commune")}{opt}</label>
      <select id="commune" value={f.commune_id} onChange={set("commune_id")}>
        <option value="">{t("account.commune.none")}</option>
        {communes.map((c) => <option key={c.id} value={c.id}>{c.nom_fr}</option>)}
      </select>
      <p className="help">{t("account.commune.help")}</p>
      <div className="row">
        <div>
          <label htmlFor="birth_date">{t("account.birthDate")}{opt}</label>
          <input id="birth_date" type="date" autoComplete="bday" value={f.birth_date} onChange={set("birth_date")} />
        </div>
        <div>
          <label htmlFor="lang">{t("account.lang")}</label>
          <select id="lang" value={f.lang} onChange={set("lang")}>
            <option value="fr">{t("account.lang.fr")}</option>
            <option value="ar">{t("account.lang.ar")}</option>
          </select>
        </div>
      </div>
      {msg && <p className={msg.ok ? "ok" : "err"} role={msg.ok ? "status" : "alert"}>{msg.text}</p>}
      <div className="actions">
        <button className="btn" disabled={busy || !f.first_name.trim() || !f.last_name.trim()}>{t("account.save")}</button>
      </div>
    </form>
  );
}

/** Changer son mot de passe (ou en choisir un : compte créé avant les mots de passe, ou mot de passe provisoire). */
function PasswordForm({ user, onSaved }: { user: User; onSaved: () => void }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const has = user.has_password !== false;

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      await api("/auth/me/password", { method: "POST", json: { current, new: next } });
      setMsg({ ok: true, text: t("account.password.changed") });
      setCurrent("");
      setNext("");
      onSaved();
    } catch (err) {
      setMsg({ ok: false, text: errText(err) });
    }
    setBusy(false);
  }

  return (
    <form onSubmit={save} noValidate>
      {!has && <p className="notice">{t("account.password.none")}</p>}
      {has && (
        <>
          <label htmlFor="pw-current">{t("account.password.current")}</label>
          <input id="pw-current" type="password" autoComplete="current-password" maxLength={128} value={current} onChange={(e) => setCurrent(e.target.value)} />
        </>
      )}
      <label htmlFor="pw-new">{t("account.password.new")}</label>
      <input id="pw-new" type="password" autoComplete="new-password" maxLength={128} value={next} onChange={(e) => setNext(e.target.value)} />
      {msg && <p className={msg.ok ? "ok" : "err"} role={msg.ok ? "status" : "alert"}>{msg.text}</p>}
      <div className="actions">
        <button className="btn btn-ghost" disabled={busy || next.length < 8 || (has && !current)}>
          {has ? t("account.password.change") : t("account.password.set")}
        </button>
      </div>
    </form>
  );
}

/** Ajout ou modification d'une voiture. Matricule déjà pris : message et signalement à l'équipe. */
function CarForm({ car, onDone, onCancel }: { car: UserCar | null; onDone: () => void; onCancel: () => void }) {
  const [plate, setPlate] = useState(car?.plate ?? "");
  const [model, setModel] = useState<Vehicle | null>(null);
  const [changeModel, setChangeModel] = useState(!car);
  const [notListed, setNotListed] = useState(Boolean(car && !car.variant_id));
  const [label, setLabel] = useState(car?.label ?? "");
  const [year, setYear] = useState(car?.year ? String(car.year) : "");
  const [nickname, setNickname] = useState(car?.nickname ?? "");
  const [mileage, setMileage] = useState(car?.mileage_km != null ? String(car.mileage_km) : "");
  const [vin, setVin] = useState(car?.vin ?? "");
  const [error, setError] = useState("");
  const [taken, setTaken] = useState(false);
  const [reportMsg, setReportMsg] = useState("");
  const [reported, setReported] = useState(false);
  const [busy, setBusy] = useState(false);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setTaken(false);
    const json: Record<string, unknown> = {
      plate, nickname: nickname || null, mileage_km: mileage ? Number(mileage) : null, vin: vin || null,
    };
    if (notListed) Object.assign(json, { variant_id: null, label, year: year ? Number(year) : null });
    else if (model) Object.assign(json, { variant_id: model.variantId, label: null, year: model.year ?? null });
    try {
      if (car) await api(`/me/vehicles/${car.id}`, { method: "PATCH", json });
      else await api("/me/vehicles", { method: "POST", json });
      onDone();
    } catch (err) {
      setTaken(err instanceof ApiError && err.code === "plate_taken");
      setError(errText(err));
    }
    setBusy(false);
  }

  async function report() {
    setBusy(true);
    try {
      await api("/me/plate-reports", { method: "POST", json: { plate, message: reportMsg || null } });
      setReported(true);
    } catch (err) {
      setError(errText(err));
    }
    setBusy(false);
  }

  const needModel = !car && !notListed && !model;
  return (
    <form className="questions" onSubmit={save} noValidate>
      <h3>{car ? car.display : t("account.cars.add")}</h3>
      <label htmlFor="plate">{t("account.cars.plate")}</label>
      <input id="plate" inputMode="numeric" autoComplete="off" required maxLength={24} placeholder={t("account.cars.plate.placeholder")}
        value={plate} onChange={(e) => { setPlate(e.target.value); setTaken(false); setReported(false); }} />
      <p className="help">{t("account.cars.plate.help")}</p>

      {!notListed && (changeModel ? (
        <VehiclePicker remember={false} onChange={setModel} />
      ) : (
        <p>
          <span className="meta">{t("account.cars.model")}</span><br /><strong>{car?.display}</strong>{" "}
          <button type="button" className="btn btn-ghost" onClick={() => setChangeModel(true)}>{t("account.cars.model.change")}</button>
        </p>
      ))}
      {model && !notListed && <p className="ok">{model.label}</p>}
      <label className="check">
        <input type="checkbox" checked={notListed} onChange={(e) => setNotListed(e.target.checked)} />
        <span>{t("account.cars.notListed")}</span>
      </label>
      {notListed && (
        <div className="row">
          <div>
            <label htmlFor="car-label">{t("account.cars.label")}</label>
            <input id="car-label" maxLength={120} placeholder={t("account.cars.label.placeholder")} value={label} onChange={(e) => setLabel(e.target.value)} />
          </div>
          <div>
            <label htmlFor="car-year">{t("account.cars.year")}</label>
            <input id="car-year" inputMode="numeric" maxLength={4} value={year} onChange={(e) => setYear(e.target.value.replace(/\D/g, ""))} />
          </div>
        </div>
      )}

      <label htmlFor="nickname">{t("account.cars.nickname")} <span className="meta">({t("account.optional")})</span></label>
      <input id="nickname" maxLength={60} placeholder={t("account.cars.nickname.placeholder")} value={nickname} onChange={(e) => setNickname(e.target.value)} />
      <label htmlFor="mileage">{t("account.cars.mileage")} <span className="meta">({t("account.optional")})</span></label>
      <input id="mileage" inputMode="numeric" maxLength={7} value={mileage} onChange={(e) => setMileage(e.target.value.replace(/\D/g, ""))} />
      <p className="help">{t("account.cars.mileage.help")}</p>
      <label htmlFor="vin">{t("account.cars.vin")} <span className="meta">({t("account.optional")})</span></label>
      <input id="vin" autoCapitalize="characters" autoComplete="off" maxLength={24} value={vin} onChange={(e) => setVin(e.target.value.toUpperCase())} />
      <p className="help">{t("account.cars.vin.help")}</p>

      {error && <p className="err" role="alert">{error}</p>}
      {taken && !reported && (
        <div>
          <label htmlFor="report-msg">{t("account.cars.taken.message")}</label>
          <input id="report-msg" maxLength={500} value={reportMsg} onChange={(e) => setReportMsg(e.target.value)} />
          <div className="actions"><button type="button" className="btn btn-ghost" disabled={busy} onClick={report}>{t("account.cars.taken.report")}</button></div>
        </div>
      )}
      {reported && <p className="ok" role="status">{t("account.cars.taken.sent")}</p>}
      <div className="actions">
        <button className="btn" disabled={busy || !plate.trim() || needModel || (notListed && !label.trim())}>{t("account.cars.save")}</button>
        <button type="button" className="btn btn-ghost" onClick={onCancel}>{t("account.cars.cancel")}</button>
      </div>
    </form>
  );
}

function Cars({ cars, reload }: { cars: UserCar[]; reload: () => void }) {
  const [editing, setEditing] = useState<UserCar | "new" | null>(cars.length ? null : "new");
  const [error, setError] = useState("");

  async function remove(c: UserCar) {
    if (!window.confirm(t("account.cars.remove.confirm"))) return;
    try {
      await api(`/me/vehicles/${c.id}`, { method: "DELETE" });
      reload();
    } catch (err) {
      setError(errText(err));
    }
  }

  return (
    <>
      {cars.length === 0 && editing === null && <p className="help">{t("account.cars.empty")}</p>}
      <ul className="list">
        {cars.map((c) => (
          <li key={c.id} className="car">
            <span>
              <strong>{c.nickname || c.display}</strong>
              {c.nickname && <><br /><span className="meta">{c.display}</span></>}
              <br />
              <span className="plate">{c.plate}</span>
              {c.mileage_km != null && <span className="meta"> · {t("account.cars.km", { km: c.mileage_km.toLocaleString("fr-FR") })}</span>}
            </span>
            <span className="actions" style={{ marginTop: 0 }}>
              <button className="btn btn-ghost" onClick={() => setEditing(c)}>{t("account.cars.edit")}</button>
              <button className="btn btn-ghost" onClick={() => remove(c)}>{t("account.cars.remove")}</button>
            </span>
          </li>
        ))}
      </ul>
      {error && <p className="err" role="alert">{error}</p>}
      {editing ? (
        <CarForm key={editing === "new" ? "new" : editing.id} car={editing === "new" ? null : editing}
          onDone={() => { setEditing(null); reload(); }} onCancel={() => setEditing(null)} />
      ) : (
        <div className="actions"><button className="btn" onClick={() => setEditing("new")}>{t("account.cars.add")}</button></div>
      )}
    </>
  );
}

function History({ cars }: { cars: UserCar[] }) {
  const [items, setItems] = useState<HistoryItem[] | null>(null);
  const [car, setCar] = useState("");
  useEffect(() => {
    api<HistoryItem[]>(`/me/diagnoses${car ? `?vehicle_id=${car}` : ""}`).then(setItems).catch(() => setItems([]));
  }, [car]);
  const name = (id: number | null) => cars.find((c) => c.id === id);
  return (
    <>
      {cars.length > 1 && (
        <select aria-label={t("account.history.allCars")} value={car} onChange={(e) => setCar(e.target.value)} style={{ maxWidth: "20rem" }}>
          <option value="">{t("account.history.allCars")}</option>
          {cars.map((c) => <option key={c.id} value={c.id}>{c.nickname || c.display}</option>)}
        </select>
      )}
      {items && items.length === 0 && <p className="help">{t("account.history.empty")}</p>}
      <ul className="list">
        {(items ?? []).map((h) => {
          const c = name(h.user_vehicle_id);
          return (
            <li key={h.session_id}>
              <span>
                <Link href={`/diagnostic/${h.session_id}`}><strong>{h.top ? `${h.top.name} → ${h.top.part}` : t("account.history.unknown")}</strong></Link>
                <br />
                <span className="meta">
                  {new Date(h.created_at).toLocaleDateString("fr-FR")}{c ? ` · ${c.nickname || c.display}` : ""} · « {h.text} »
                </span>
              </span>
            </li>
          );
        })}
      </ul>
    </>
  );
}

/** Mon compte : informations, voitures, historique, déconnexion, suppression (loi 18-07, section 10 du cahier). */
function Account() {
  const router = useRouter();
  const params = useSearchParams();
  const welcome = params.get("bienvenue") === "1";
  const next = params.get("next");
  const [user, setUser] = useState<User | null>(null);
  const [cars, setCars] = useState<UserCar[] | null>(null);
  const [ready, setReady] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const loadCars = useCallback(() => { api<UserCar[]>("/me/vehicles").then(setCars).catch(() => setCars([])); }, []);
  useEffect(() => {
    const u = session.user();
    setUser(u);
    setReady(true);
    if (u) {
      loadCars();
      api<User>("/auth/me").then((fresh) => setUser({ ...u, ...fresh })).catch(() => undefined);
    }
  }, [loadCars]);

  async function remove() {
    if (!window.confirm(t("account.delete.confirm"))) return;
    try {
      await api("/auth/me", { method: "DELETE" });
      session.clear();
      setUser(null);
      setDone(true);
    } catch (e) {
      setError(errText(e));
    }
  }

  if (!ready) return <p>{t("common.loading")}</p>;
  if (done) return (<section><h1>{t("account.title")}</h1><p className="ok" role="status">{t("account.deleted")}</p></section>);
  if (!user) {
    return (
      <section>
        <h1>{t("account.title")}</h1>
        <p>{t("account.loginFirst")}</p>
        <Link className="btn" href="/connexion?next=/compte">{t("nav.login")}</Link>
      </section>
    );
  }
  const complete = Boolean(user.first_name && user.last_name);
  return (
    <section>
      {welcome ? (
        <>
          <h1>{t("account.welcome.title")}</h1>
          <p className="lead">{complete ? t("account.welcome.cars") : t("account.welcome.text")}</p>
        </>
      ) : (
        <h1>{t("account.title")}</h1>
      )}

      <h2 className="section">{t("account.profile")}</h2>
      <ProfileForm user={user} onSaved={setUser} />

      {complete && (
        <>
          <h2 className="section">{t("account.cars")}</h2>
          {cars ? <Cars cars={cars} reload={loadCars} /> : <p>{t("common.loading")}</p>}
          {welcome && next && next !== "/compte" && (
            <div className="actions"><button className="btn btn-primary" onClick={() => router.push(next)}>{t("account.continue")}</button></div>
          )}

          <h2 className="section">{t("account.history")}</h2>
          <History cars={cars ?? []} />
        </>
      )}

      <h2 className="section">{t("account.password")}</h2>
      <PasswordForm user={user} onSaved={() => setUser({ ...user, has_password: true })} />

      <p className="section"><span className="meta">{t("account.role")}</span><br /><strong>{t(`account.role.${user.role}`)}</strong></p>
      <div className="actions">
        <button className="btn btn-ghost" onClick={() => { session.clear(); setUser(null); }}>{t("nav.logout")}</button>
      </div>
      <h2 className="section">{t("account.delete.title")}</h2>
      <p className="help">{t("account.delete.text")}</p>
      {error && <p className="err" role="alert">{error}</p>}
      <div className="actions">
        <button className="btn" onClick={remove}>{t("account.delete.button")}</button>
      </div>
    </section>
  );
}

export default function AccountPage() {
  return (
    <Suspense fallback={null}>
      <Account />
    </Suspense>
  );
}
