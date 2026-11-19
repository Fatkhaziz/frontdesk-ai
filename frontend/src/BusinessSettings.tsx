import { useEffect, useState } from "react";
import { Api, Run, dollarsToCents } from "./domain";
import { BusinessProfile, Workspace, exampleProfile } from "./business";

export default function BusinessSettings({
  workspace,
  api,
  run,
  busy,
  refresh,
  notify,
}: {
  workspace: Workspace;
  api: Api;
  run: Run;
  busy: boolean;
  refresh: () => Promise<void>;
  notify: (message: string) => void;
}) {
  const [profile, setProfile] = useState<BusinessProfile>(() =>
    structuredClone(
      workspace.profile || exampleProfile(workspace.name, "dealership"),
    ),
  );
  const [approved, setApproved] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [priceErrors, setPriceErrors] = useState<Record<string, boolean>>({});
  const [priceInputs, setPriceInputs] = useState<Record<string, string>>({});
  useEffect(() => {
    setProfile(
      structuredClone(
        workspace.profile || exampleProfile(workspace.name, "dealership"),
      ),
    );
    setApproved(false);
    setDirty(false);
    setPriceErrors({});
    setPriceInputs({});
  }, [workspace.id, workspace.revision, workspace.published_revision]);
  function change(next: BusinessProfile) {
    setProfile(next);
    setDirty(true);
    setApproved(false);
  }
  function useExample(domain: BusinessProfile['domain']) {
    change(exampleProfile(profile.name, domain));
    setPriceErrors({});
    setPriceInputs({});
  }
  const owner = workspace.role === "owner";
  return (
    <section>
      <div className="section-heading">
        <div>
          <h2>Business settings</h2>
          <p className="muted">
            Save a private draft, then review and publish the settings customers
            will see.
          </p>
        </div>
        {workspace.published_revision && (
          <a
            className="button primary"
            href={"/business/" + workspace.id}
            target="_blank"
            rel="noreferrer"
          >
            View business page
          </a>
        )}
      </div>
      <p>
        Saved revision {workspace.revision || "none"} · Published revision{" "}
        {workspace.published_revision || "none"}
      </p>
      {!owner && (
        <p className="notice">
          You can view these settings. A business owner can edit and publish
          them.
        </p>
      )}
      <fieldset disabled={!owner || busy}>
        <div className="actions">
          <button
            type="button"
            onClick={() => useExample('dealership')}
          >
            Use dealership example
          </button>
          <button
            type="button"
            onClick={() => useExample('salon')}
          >
            Use salon example
          </button>
        </div>
        <small>
          Examples fill a private form. Review the contact, services and
          policies before publishing.
        </small>
        <div className="field-grid">
          <label>
            Business name
            <input
              required
              maxLength={120}
              value={profile.name}
              onChange={(e) => change({ ...profile, name: e.target.value })}
            />
          </label>
          <label>
            Business type
            <select
              value={profile.domain}
              onChange={(e) =>
                change({
                  ...profile,
                  domain: e.target.value as BusinessProfile["domain"],
                })
              }
            >
              <option value="dealership">Dealership</option>
              <option value="salon">Salon</option>
            </select>
          </label>
          <label>
            Public contact
            <input
              maxLength={300}
              value={profile.contact}
              onChange={(e) => change({ ...profile, contact: e.target.value })}
            />
          </label>
          <label>
            Time zone
            <input
              value={profile.time_zone}
              onChange={(e) =>
                change({ ...profile, time_zone: e.target.value })
              }
            />
          </label>
        </div>
        <label>
          About the business
          <textarea
            maxLength={1200}
            value={profile.about}
            onChange={(e) => change({ ...profile, about: e.target.value })}
          />
        </label>
        <h3>Opening hours</h3>
        {profile.hours.map((day, index) => (
          <div className="hours-row" key={day.day}>
            <strong>{day.day}</strong>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={day.opens === null}
                onChange={(e) =>
                  change({
                    ...profile,
                    hours: profile.hours.map((d, i) =>
                      i === index
                        ? {
                            ...d,
                            opens: e.target.checked ? null : "09:00",
                            closes: e.target.checked ? null : "17:00",
                          }
                        : d,
                    ),
                  })
                }
              />
              Closed
            </label>
            {day.opens !== null && (
              <>
                <label>
                  Opens {day.day}
                  <input
                    type="time"
                    value={day.opens}
                    onChange={(e) =>
                      change({
                        ...profile,
                        hours: profile.hours.map((d, i) =>
                          i === index ? { ...d, opens: e.target.value } : d,
                        ),
                      })
                    }
                  />
                </label>
                <label>
                  Closes {day.day}
                  <input
                    type="time"
                    value={day.closes || ""}
                    onChange={(e) =>
                      change({
                        ...profile,
                        hours: profile.hours.map((d, i) =>
                          i === index ? { ...d, closes: e.target.value } : d,
                        ),
                      })
                    }
                  />
                </label>
              </>
            )}
          </div>
        ))}
        <h3>Services and inquiry questions</h3>
        <p className="muted">
          These forms collect requests for staff. They do not reserve
          appointments.
        </p>
        {profile.services.map((service, index) => (
          <div className="settings-item" key={service.id}>
            <label>
              Service name
              <input
                maxLength={100}
                value={service.name}
                onChange={(e) =>
                  change({
                    ...profile,
                    services: profile.services.map((s, i) =>
                      i === index ? { ...s, name: e.target.value } : s,
                    ),
                  })
                }
              />
            </label>
            <label>
              Service description
              <input
                maxLength={700}
                value={service.description}
                onChange={(e) =>
                  change({
                    ...profile,
                    services: profile.services.map((s, i) =>
                      i === index ? { ...s, description: e.target.value } : s,
                    ),
                  })
                }
              />
            </label>
            <div className="field-grid">
              <label>
                Typical duration in minutes
                <input
                  type="number"
                  min={5}
                  max={1440}
                  value={service.duration_minutes}
                  onChange={(e) =>
                    change({
                      ...profile,
                      services: profile.services.map((s, i) =>
                        i === index
                          ? { ...s, duration_minutes: Number(e.target.value) }
                          : s,
                      ),
                    })
                  }
                />
              </label>
              <label>
                Price in USD, blank for staff quote
                <input
                  type="number"
                  min={0}
                  step="0.01"
                  value={priceInputs[service.id] ?? (service.price_cents === null ? '' : String(service.price_cents / 100))}
                  key={service.id + ":" + workspace.revision}
                  onChange={(e) => {
                    setPriceInputs(inputs => ({ ...inputs, [service.id]: e.target.value }));
                    setDirty(true);
                    setApproved(false);
                    try {
                      const price =
                        e.target.value === ""
                          ? null
                          : dollarsToCents(e.target.value);
                      change({
                        ...profile,
                        services: profile.services.map((s, i) =>
                          i === index ? { ...s, price_cents: price } : s,
                        ),
                      });
                      setPriceErrors(errors => ({ ...errors, [service.id]: false }));
                    } catch (error) {
                      setPriceErrors(errors => ({ ...errors, [service.id]: true }));
                      notify(
                        error instanceof Error
                          ? error.message
                          : "Enter a valid price.",
                      );
                    }
                  }}
                />
              </label>
            </div>
            {service.questions.map((question, qIndex) => (
              <div className="question-row" key={question.id}>
                <label>
                  Question {qIndex + 1}
                  <input
                    maxLength={160}
                    value={question.label}
                    onChange={(e) =>
                      change({
                        ...profile,
                        services: profile.services.map((s, i) =>
                          i === index
                            ? {
                                ...s,
                                questions: s.questions.map((q, j) =>
                                  j === qIndex
                                    ? { ...q, label: e.target.value }
                                    : q,
                                ),
                              }
                            : s,
                        ),
                      })
                    }
                  />
                </label>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={question.required}
                    onChange={(e) =>
                      change({
                        ...profile,
                        services: profile.services.map((s, i) =>
                          i === index
                            ? {
                                ...s,
                                questions: s.questions.map((q, j) =>
                                  j === qIndex
                                    ? { ...q, required: e.target.checked }
                                    : q,
                                ),
                              }
                            : s,
                        ),
                      })
                    }
                  />
                  Required
                </label>
                <button
                  onClick={() =>
                    change({
                      ...profile,
                      services: profile.services.map((s, i) =>
                        i === index
                          ? {
                              ...s,
                              questions: s.questions.filter(
                                (_, j) => j !== qIndex,
                              ),
                            }
                          : s,
                      ),
                    })
                  }
                >
                  Remove question
                </button>
              </div>
            ))}
            <div className="actions">
              <button
                disabled={service.questions.length >= 12}
                onClick={() =>
                  change({
                    ...profile,
                    services: profile.services.map((s, i) =>
                      i === index
                        ? {
                            ...s,
                            questions: [
                              ...s.questions,
                              {
                                id: "q-" + crypto.randomUUID().slice(0, 8),
                                label: "",
                                required: true,
                              },
                            ],
                          }
                        : s,
                    ),
                  })
                }
              >
                Add inquiry question
              </button>
              <button
                className="danger"
                disabled={profile.services.length === 1}
                onClick={() =>
                  change({
                    ...profile,
                    services: profile.services.filter((_, i) => i !== index),
                  })
                }
              >
                Remove service
              </button>
            </div>
          </div>
        ))}
        <button
          disabled={profile.services.length >= 20}
          onClick={() =>
            change({
              ...profile,
              services: [
                ...profile.services,
                {
                  id: "service-" + crypto.randomUUID().slice(0, 8),
                  name: "",
                  description: "",
                  duration_minutes: 30,
                  price_cents: null,
                  questions: [],
                },
              ],
            })
          }
        >
          Add service
        </button>
        <h3>Approved answers</h3>
        <p className="muted">
          Customers can select one of these questions. The answer comes directly
          from your published settings.
        </p>
        {profile.faqs.map((faq, index) => (
          <div className="settings-item" key={index}>
            <label>
              FAQ question
              <input
                maxLength={200}
                value={faq.question}
                onChange={(e) =>
                  change({
                    ...profile,
                    faqs: profile.faqs.map((f, i) =>
                      i === index ? { ...f, question: e.target.value } : f,
                    ),
                  })
                }
              />
            </label>
            <label>
              FAQ answer
              <textarea
                maxLength={1200}
                value={faq.answer}
                onChange={(e) =>
                  change({
                    ...profile,
                    faqs: profile.faqs.map((f, i) =>
                      i === index ? { ...f, answer: e.target.value } : f,
                    ),
                  })
                }
              />
            </label>
            <button
              onClick={() =>
                change({
                  ...profile,
                  faqs: profile.faqs.filter((_, i) => i !== index),
                })
              }
            >
              Remove FAQ
            </button>
          </div>
        ))}
        <button
          disabled={profile.faqs.length >= 30}
          onClick={() =>
            change({
              ...profile,
              faqs: [...profile.faqs, { question: "", answer: "" }],
            })
          }
        >
          Add FAQ
        </button>
        <div className="saved-summary">
          <button
            className="primary"
            disabled={profile.services.some(service => priceErrors[service.id])}
            onClick={() =>
              run(async () => {
                await api("/business/profile", "PUT", {
                  expected_revision: workspace.revision,
                  profile,
                });
                await refresh();
                notify(
                  "Private business settings saved. Review them before publishing.",
                );
              })
            }
          >
            Save private settings
          </button>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={approved}
              disabled={dirty || workspace.revision === 0}
              onChange={(e) => setApproved(e.target.checked)}
            />
            I reviewed the saved settings and approve this revision for
            customers.
          </label>
          <div className="actions">
            <button
              className="primary"
              disabled={dirty || !approved || workspace.revision === 0}
              onClick={() =>
                run(async () => {
                  await api("/business/profile/publish", "POST", {
                    expected_revision: workspace.revision,
                    confirm_approval: true,
                  });
                  await refresh();
                  notify(
                    "Approved business settings published. Open View business page to test them.",
                  );
                })
              }
            >
              Publish approved settings
            </button>
            {workspace.published_revision && (
              <button
                onClick={() =>
                  run(async () => {
                    await api("/business/profile/unpublish", "POST");
                    await refresh();
                    notify("Business page unpublished.");
                  })
                }
              >
                Unpublish business page
              </button>
            )}
          </div>
          {dirty && <p>Save your changes before approving them.</p>}
        </div>
      </fieldset>
    </section>
  );
}
