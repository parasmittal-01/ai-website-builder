import React, { useState } from "react";
import { generateProject } from "./api";
import ProjectPreview from "./components/ProjectPreview";
import "./index.css";
import "./App.css";

const promptStarters = [
  "A cozy neighborhood coffee shop",
  "A portfolio for a ceramic artist",
  "A playful task planner for students",
];

export default function App() {
  const [description, setDescription] = useState("");
  const [projectId, setProjectId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async (event) => {
    event.preventDefault();
    if (!description.trim() || loading) return;

    setLoading(true);
    setError("");

    try {
      const result = await generateProject(description);
      if (!result?.project_id) {
        throw new Error(result?.error || "The server did not return a project ID.");
      }
      setProjectId(result.project_id);
    } catch (err) {
      const message = err.response?.data?.error || err.message || "Unknown error";
      setError(message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="builder-app">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Sitecraft home">
          <span className="brand-mark" aria-hidden="true">S</span>
          <span className="brand-name">sitecraft</span>
          <span className="brand-divider" aria-hidden="true" />
          <span className="brand-caption">AI WEBSITE BUILDER</span>
        </a>
        <div className="workspace-status"><span className="status-dot" />Your creative workspace</div>
      </header>

      <main className="workspace-layout">
        <section className="composer-panel" aria-labelledby="builder-title">
          <div className="composer-content">
            <div className="eyebrow"><span className="eyebrow-line" />A LITTLE IDEA GOES A LONG WAY</div>
            <h1 id="builder-title">Let's make a site that feels like <span>you.</span></h1>
            <p className="intro-copy">Tell us what you have in mind. Our AI will turn your words into a website you can explore and take with you.</p>

            <form className="prompt-form" onSubmit={handleGenerate}>
              <label className="field-label" htmlFor="site-prompt">YOUR WEBSITE IDEA</label>
              <div className="prompt-field">
                <textarea
                  id="site-prompt"
                  placeholder="A bright, welcoming website for my neighborhood bakery..."
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  onKeyDown={(event) => {
                    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                      handleGenerate(event);
                    }
                  }}
                  aria-describedby="prompt-hint prompt-count"
                  maxLength={4000}
                />
                <div className="prompt-meta">
                  <span id="prompt-hint">Be as specific or imaginative as you like.</span>
                  <span id="prompt-count">{description.length}/4000</span>
                </div>
              </div>

              <div className="starter-area">
                <span className="starter-label">NEED A SPARK?</span>
                <div className="starter-list">
                  {promptStarters.map((starter) => (
                    <button
                      className="starter-chip"
                      key={starter}
                      type="button"
                      onClick={() => {
                        setDescription(starter);
                        setError("");
                      }}
                    >
                      <span aria-hidden="true">+</span>{starter}
                    </button>
                  ))}
                </div>
              </div>

              {error && <div className="error-message" role="alert">{error}</div>}

              <div className="submit-row">
                <button className="generate-button" type="submit" disabled={loading || !description.trim()}>
                  <span>{loading ? "Making your website" : "Make my website"}</span>
                  <span className={`button-arrow${loading ? " is-loading" : ""}`} aria-hidden="true">{loading ? "..." : "→"}</span>
                </button>
                <span className="keyboard-hint">or press <kbd>Ctrl</kbd> <kbd>Enter</kbd></span>
              </div>
            </form>
          </div>

          <div className="composer-footer">
            <span className="footer-spark" aria-hidden="true">✳</span>
            <span>MADE WITH CURIOSITY <i /> BUILT WITH Efforts</span>
          </div>
        </section>

        <section className="preview-panel" aria-label="Website preview">
          <div className="preview-panel-top">
            <div className="preview-heading">
              <span className="preview-kicker">YOUR CANVAS</span>
              <span className="preview-title">{projectId ? "The first look" : "A new page awaits"}</span>
            </div>
            <span className={`preview-state${projectId ? " is-live" : ""}`}>
              <span className="status-dot" />{projectId ? "READY TO EXPLORE" : "PREVIEW"}
            </span>
          </div>

          {projectId ? (
            <ProjectPreview projectId={projectId} loading={loading} />
          ) : (
            <div className={`empty-preview${loading ? " is-generating" : ""}`}>
              <div className="browser-window" aria-hidden="true">
                <div className="browser-bar">
                  <span /><span /><span />
                  <div className="browser-address">your-new-site.com</div>
                </div>
                <div className="mock-site">
                  <div className="mock-nav"><span className="mock-logo" /><span /><span /><span className="mock-nav-button" /></div>
                  <div className="mock-hero">
                    <div className="mock-copy"><i /><b /><b /><span /></div>
                    <div className="mock-art"><div /><span /></div>
                  </div>
                  <div className="mock-cards"><i /><i /><i /></div>
                </div>
              </div>
              <div className="canvas-caption">
                <span className="canvas-star" aria-hidden="true">✳</span>
                <div>
                  <strong>{loading ? "Your idea is taking shape" : "A blank canvas, full of possibility"}</strong>
                  <span>{loading ? "Putting the pieces together..." : "Every good website starts somewhere."}</span>
                </div>
              </div>
              {loading && <div className="preview-progress" aria-label="Generating your website"><span /></div>}
            </div>
          )}

          <div className="preview-panel-footer">
            <span><i className="footer-dot" /> HTML, CSS &amp; JS</span>
            <span>YOURS TO KEEP <b aria-hidden="true">↗</b></span>
          </div>
        </section>
      </main>
    </div>
  );
}
