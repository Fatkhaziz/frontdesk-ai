import { useEffect, useRef, useState } from "react";
import { Api, money } from "./domain";
import { BusinessProfile } from "./business";

export default function PublicBusiness({ id, api }: { id: string; api: Api }) {
  const [profile, setProfile] = useState<
    (BusinessProfile & { revision: number }) | null
  >(null);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState(""),
    [answer, setAnswer] = useState("");
  const [evidence, setEvidence] = useState<{ mode: string; reason?: string; revision?: number; handoff: boolean; sources: { id: string; text: string; label: string; revision: number }[] } | null>(null);
  const [serviceId, setServiceId] = useState(""),
    [answers, setAnswers] = useState<Record<string, string>>({});
  const [message, setMessage] = useState(""),
    [contact, setContact] = useState(""),
    [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const locked = useRef(false);
  const requestKey = useRef(crypto.randomUUID());
  useEffect(() => {
    api("/public/businesses/" + id)
      .then(setProfile)
      .catch(() => setError("This business page is unavailable."));
  }, [id]);
  const service = profile?.services.find((s) => s.id === serviceId);
  async function ask(event: React.FormEvent) {
    event.preventDefault();
    if (locked.current || !question.trim()) return;
    locked.current = true;
    setBusy(true);
    setError("");
    setAnswer("");
    setEvidence(null);
    try {
      const result = await api(
        "/public/businesses/" + id + "/questions",
        "POST",
        { question },
      );
      setAnswer(result.answer);
      setEvidence({ ...result, sources: result.sources || [] });
      if (result.handoff) setMessage(question);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Please try again.");
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (locked.current || !profile) return;
    locked.current = true;
    setBusy(true);
    setError("");
    try {
      await api("/public/businesses/" + id + "/inquiries", "POST", {
        expected_revision: profile.revision,
        service_id: serviceId || null,
        answers,
        message,
        contact,
        request_key: requestKey.current,
      });
      setNotice(
        "Your inquiry is saved in this business’s staff inbox. Staff will arrange any next steps. No appointment has been reserved.",
      );
      setMessage("");
      setContact("");
      setAnswers({});
      setServiceId("");
      requestKey.current = crypto.randomUUID();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Your inquiry was not saved. Please try again.",
      );
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }
  return (
    <>
      {error && (
        <p className="notice" role="alert">
          {error}
        </p>
      )}
      {profile && (
        <>
          <div className="public-hero">
            <p className="eyebrow">
              {profile.domain === "photography_studio" ? "Photography studio" : profile.domain === "salon" ? "Salon" : "Dealership"}
            </p>
            <h1>{profile.name}</h1>
            <p className="lead">{profile.about}</p>
            <p>{profile.contact}</p>
          </div>
          <div className="public-layout">
            <div>
              <section>
                <h2>Services</h2>
                {profile.services.map((s) => (
                  <article className="service-card" key={s.id}>
                    <h3>{s.name}</h3>
                    <p>{s.description}</p>
                    <p>
                      {s.duration_minutes} minutes ·{" "}
                      {s.price_cents === null
                        ? "Ask staff for a quote"
                        : money(s.price_cents)}
                    </p>
                    <button
                      onClick={() => {
                        setServiceId(s.id);
                        setAnswers({});
                        requestKey.current = crypto.randomUUID();
                        document
                          .getElementById("business-inquiry")
                          ?.scrollIntoView({ block: "start" });
                      }}
                    >
                      Inquire about {s.name}
                    </button>
                  </article>
                ))}
              </section>
              <section>
                <h2>Opening hours</h2>
                <p className="muted">All times use {profile.time_zone}.</p>
                <dl className="opening-hours">
                  {profile.hours.map((day) => (
                    <div key={day.day}>
                      <dt>{day.day}</dt>
                      <dd>
                        {day.opens === null
                          ? "Closed"
                          : day.opens + "–" + day.closes}
                      </dd>
                    </div>
                  ))}
                </dl>
              </section>
            </div>
            <div>
              <section>
                <h2>Ask this business</h2>
                <p>
                  Ask in your own words. When live AI is enabled, it selects
                  published statements; otherwise, questions use exact FAQ matching.
                  Sources and the answering mode appear below. Send contact details
                  only in the separate inquiry form.
                </p>
                <div className="faq-options">
                  {profile.faqs.map((faq) => (
                    <button
                      key={faq.question}
                      onClick={() => setQuestion(faq.question)}
                    >
                      {faq.question}
                    </button>
                  ))}
                </div>
                <form onSubmit={ask}>
                  <label>
                    Your question
                    <input
                      maxLength={1000}
                      required
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                    />
                  </label>
                  <button className="primary" disabled={busy}>
                    {busy ? "Checking…" : "Check approved answer"}
                  </button>
                </form>
                {answer && (
                  <p role="status" className="saved-summary">
                    {answer}
                  </p>
                )}
                {evidence && <div id="published-sources" className="saved-summary">
                  <strong>{({ live_ai: "Live AI · checked published evidence", exact_match: "Exact FAQ matching · no AI call", fallback: "Fallback · staff review needed", error: "Error · answer unavailable" } as Record<string, string>)[evidence.mode] || "Staff review"}</strong>
                  <p>Published revision {evidence.revision}. {evidence.handoff ? "Staff follow-up is offered; no inquiry has been sent." : "Published source statements:"}</p>
                  {evidence.reason && evidence.mode === "error" && <p>Please retry or send an inquiry to staff.</p>}
                  <ul>{evidence.sources.map(source => <li key={source.id}><strong>{source.label} · revision {source.revision}</strong><blockquote>{source.text}</blockquote></li>)}</ul>
                </div>}
              </section>
              <section id="business-inquiry">
                <h2>Send an inquiry</h2>
                <p>Choose a service and share details for staff follow-up.</p>
                <form onSubmit={submit}>
                  <label>
                    Service
                    <select
                      aria-label="Service"
                      value={serviceId}
                      onChange={(e) => {
                        setServiceId(e.target.value);
                        setAnswers({});
                        requestKey.current = crypto.randomUUID();
                      }}
                    >
                      <option value="">General inquiry</option>
                      {profile.services.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  {service?.questions.map((q) => (
                    <label key={q.id}>
                      {q.label}
                      {q.required ? " (required)" : " (optional)"}
                      <input
                        required={q.required}
                        maxLength={500}
                        value={answers[q.id] || ""}
                        onChange={(e) => {
                          const next = { ...answers };
                          if (e.target.value.trim())
                            next[q.id] = e.target.value;
                          else delete next[q.id];
                          setAnswers(next);
                        }}
                      />
                    </label>
                  ))}
                  <label>
                    Message
                    <textarea
                      required
                      maxLength={1000}
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                    />
                  </label>
                  <label>
                    Your email or phone
                    <input
                      required
                      minLength={3}
                      maxLength={300}
                      value={contact}
                      onChange={(e) => setContact(e.target.value)}
                    />
                  </label>
                  <small>
                    Share contact details voluntarily for this business to
                    follow up. This demo sends no email or phone notification.
                  </small>
                  <button className="primary" disabled={busy}>
                    {busy ? "Saving…" : "Send inquiry to staff"}
                  </button>
                </form>
                {notice && (
                  <p className="notice success" role="status">
                    {notice}
                  </p>
                )}
              </section>
            </div>
          </div>
        </>
      )}
      {!profile && !error && <p role="status">Loading business…</p>}
    </>
  );
}
