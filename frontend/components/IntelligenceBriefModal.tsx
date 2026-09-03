"use client";
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowDownToLine,
  CheckCircle2,
  FileText,
  LoaderCircle,
  Radio,
  Share2,
  ShieldCheck,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";
import { getIntelligenceBrief } from "@/lib/api";
import type { IntelligenceBrief } from "@/types";

export function IntelligenceBriefModal({
  topicSlug,
  isOpen,
  onClose,
}: {
  topicSlug?: string;
  isOpen: boolean;
  onClose: () => void;
}) {
  const [brief, setBrief] = useState<IntelligenceBrief | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      getIntelligenceBrief(topicSlug)
        .then(setBrief)
        .catch(() => setBrief(null))
        .finally(() => setLoading(false));
    }
  }, [isOpen, topicSlug]);

  if (!isOpen) return null;

  function downloadReport() {
    if (!brief) return;
    const text = `
=====================================================
${brief.title.toUpperCase()}
Generated: ${brief.generated_at}
=====================================================

1. EXECUTIVE SUMMARY:
${brief.executive_summary.map((s, i) => `  [${i + 1}] ${s}`).join("\n")}

2. EMERGING NARRATIVES:
${brief.emerging_narratives.map((n) => `  * ${n.label} (Score: ${n.momentum_score}/100, Status: ${n.status})`).join("\n")}

3. PUBLIC SENTIMENT DISTRIBUTION:
  * Opposing: ${brief.sentiment_overview.negative ?? 0}%
  * Neutral:  ${brief.sentiment_overview.neutral ?? 0}%
  * Supportive: ${brief.sentiment_overview.positive ?? 0}%

4. EMOTIONAL SIGNALS:
${Object.entries(brief.emotion_overview).map(([k, v]) => `  * ${k}: ${v}%`).join("\n")}

5. STANCE ASSESSMENT:
  * Support: ${brief.stance_overview?.support_pct ?? 0}%
  * Oppose:  ${brief.stance_overview?.oppose_pct ?? 0}%
  * Neutral: ${brief.stance_overview?.neutral_pct ?? 0}%

6. INFLUENCERS & OPINION DRIVERS:
${brief.influencers.map((inf) => `  * ${inf.author} (PageRank: ${inf.pagerank_score}, Group: ${inf.group})`).join("\n")}

7. RISK MONITOR:
${brief.risk_signals.map((r) => `  * [${r.level}] ${r.reason} (Trend: ${r.trend})`).join("\n")}

8. CROSS-PLATFORM DIFFUSION:
  ${brief.cross_platform_movement.timeline_summary}

9. ANALYST ASSESSMENT:
${brief.analyst_assessment}

10. RECOMMENDED ATTENTION:
${brief.recommended_attention}
=====================================================
    `.trim();

    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `updates-intelligence-brief-${topicSlug || "global"}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(10, 10, 16, 0.8)",
        backdropFilter: "blur(6px)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "1.5rem",
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#1e2030",
          border: "1px solid rgba(138, 173, 244, 0.3)",
          borderRadius: "14px",
          width: "100%",
          maxWidth: "850px",
          maxHeight: "90vh",
          overflowY: "auto",
          padding: "1.75rem",
          color: "#cad3f5",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.6)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.08)", paddingBottom: "1rem", marginBottom: "1.25rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <FileText size={24} style={{ color: "#8aadf4" }} />
            <div>
              <h2 style={{ margin: 0, fontSize: "1.25rem", color: "#cad3f5" }}>
                {brief?.title || "Automated Intelligence Brief"}
              </h2>
              <small style={{ color: "#a5adcb" }}>Generated: {brief?.generated_at || "Recent"}</small>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            {brief && (
              <button
                onClick={downloadReport}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem",
                  padding: "6px 12px",
                  borderRadius: "6px",
                  background: "rgba(138, 173, 244, 0.2)",
                  color: "#8aadf4",
                  border: "1px solid rgba(138, 173, 244, 0.4)",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                }}
              >
                <ArrowDownToLine size={14} /> Download Brief
              </button>
            )}
            <button
              onClick={onClose}
              style={{
                background: "transparent",
                border: "none",
                color: "#a5adcb",
                cursor: "pointer",
                padding: "4px",
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: "3rem 1rem", color: "#a5adcb" }}>
            <LoaderCircle size={28} className="spin" style={{ color: "#8aadf4", marginBottom: "0.75rem" }} />
            <p>Aggregating multi-model intelligence brief...</p>
          </div>
        ) : brief ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {/* 1. Executive Summary */}
            <div>
              <h3 style={{ fontSize: "0.95rem", textTransform: "uppercase", color: "#8aadf4", margin: "0 0 0.5rem 0", letterSpacing: "0.5px" }}>
                1. Executive Summary
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                {brief.executive_summary.map((item, idx) => (
                  <div key={idx} style={{ padding: "0.5rem 0.75rem", background: "rgba(24, 25, 38, 0.6)", borderRadius: "6px", fontSize: "0.85rem", borderLeft: "3px solid #8aadf4" }}>
                    {item}
                  </div>
                ))}
              </div>
            </div>

            {/* 2. Sentiment & Emotion Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <div style={{ padding: "0.75rem", background: "rgba(24, 25, 38, 0.6)", borderRadius: "8px" }}>
                <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.85rem", color: "#eed49f" }}>Sentiment Distribution (SentiMix)</h4>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem" }}>
                  <span style={{ color: "#ed8796" }}>Oppose: {brief.sentiment_overview.negative ?? 0}%</span>
                  <span style={{ color: "#eed49f" }}>Neutral: {brief.sentiment_overview.neutral ?? 0}%</span>
                  <span style={{ color: "#a6da95" }}>Support: {brief.sentiment_overview.positive ?? 0}%</span>
                </div>
              </div>
              <div style={{ padding: "0.75rem", background: "rgba(24, 25, 38, 0.6)", borderRadius: "8px" }}>
                <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.85rem", color: "#8aadf4" }}>Stance Assessment</h4>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem" }}>
                  <span style={{ color: "#a6da95" }}>Support: {brief.stance_overview?.support_pct ?? 0}%</span>
                  <span style={{ color: "#ed8796" }}>Oppose: {brief.stance_overview?.oppose_pct ?? 0}%</span>
                  <span style={{ color: "#a5adcb" }}>Neutral: {brief.stance_overview?.neutral_pct ?? 0}%</span>
                </div>
              </div>
            </div>

            {/* 3. Emerging Narratives */}
            <div>
              <h3 style={{ fontSize: "0.95rem", textTransform: "uppercase", color: "#8aadf4", margin: "0 0 0.5rem 0" }}>
                2. Emerging Narratives (BERTopic + c-TF-IDF)
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "0.5rem" }}>
                {brief.emerging_narratives.map((n) => (
                  <div key={n.topic_id} style={{ padding: "0.5rem 0.75rem", background: "rgba(24, 25, 38, 0.6)", borderRadius: "6px", fontSize: "0.8rem" }}>
                    <strong style={{ color: "#cad3f5", display: "block" }}>{n.label}</strong>
                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px", color: "#a5adcb" }}>
                      <span>Score: {n.momentum_score}/100</span>
                      <span style={{ color: "#eed49f" }}>{n.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 4. Top Influencers (PageRank) */}
            <div>
              <h3 style={{ fontSize: "0.95rem", textTransform: "uppercase", color: "#8aadf4", margin: "0 0 0.5rem 0" }}>
                3. Lead Opinion Amplifiers (NetworkX PageRank)
              </h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {brief.influencers.map((inf) => (
                  <span
                    key={inf.author}
                    style={{
                      padding: "4px 10px",
                      borderRadius: "999px",
                      background: "rgba(138, 173, 244, 0.15)",
                      color: "#8aadf4",
                      fontSize: "0.78rem",
                      border: "1px solid rgba(138, 173, 244, 0.3)",
                    }}
                  >
                    #{inf.rank} {inf.author} (PageRank: {inf.pagerank_score})
                  </span>
                ))}
              </div>
            </div>

            {/* 5. Cross-Platform Diffusion */}
            <div>
              <h3 style={{ fontSize: "0.95rem", textTransform: "uppercase", color: "#8aadf4", margin: "0 0 0.5rem 0" }}>
                4. Cross-Platform Diffusion
              </h3>
              <p style={{ margin: 0, padding: "0.5rem 0.75rem", background: "rgba(24, 25, 38, 0.6)", borderRadius: "6px", fontSize: "0.85rem", color: "#cad3f5" }}>
                {brief.cross_platform_movement.timeline_summary}
              </p>
            </div>

            {/* 6. Analyst Assessment & Recommended Attention */}
            <div style={{ padding: "0.75rem 1rem", background: "rgba(138, 173, 244, 0.08)", borderRadius: "8px", border: "1px solid rgba(138, 173, 244, 0.2)" }}>
              <strong style={{ display: "block", color: "#8aadf4", fontSize: "0.85rem", marginBottom: "0.25rem" }}>
                Analyst Assessment & Recommended Action:
              </strong>
              <p style={{ margin: "0 0 0.5rem 0", fontSize: "0.82rem", lineHeight: 1.4 }}>
                {brief.analyst_assessment}
              </p>
              <small style={{ color: "#eed49f", display: "block", fontSize: "0.78rem" }}>
                Next steps: {brief.recommended_attention}
              </small>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "2rem", color: "#8087a2" }}>
            <AlertTriangle size={24} style={{ color: "#eed49f", marginBottom: "0.5rem" }} />
            <p>Insufficient data to generate an automated intelligence brief for this topic.</p>
          </div>
        )}
      </div>
    </div>
  );
}
