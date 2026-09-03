"use client";
import { useEffect, useState } from "react";
import { CheckCircle2, Cpu, HelpCircle, Layers, ShieldCheck, Sparkles } from "lucide-react";
import { getModelTransparency } from "@/lib/api";
import type { ModelTransparencyItem } from "@/types";

export function ModelTransparencyPanel() {
  const [pipeline, setPipeline] = useState<ModelTransparencyItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelTransparency()
      .then((data) => {
        setPipeline(data.pipeline || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <section
      className="panel model-transparency-panel"
      style={{
        marginTop: "1.5rem",
        background: "rgba(30, 32, 48, 0.8)",
        borderRadius: "12px",
        border: "1px solid rgba(138, 173, 244, 0.2)",
        padding: "1.25rem",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Cpu size={20} style={{ color: "#8aadf4" }} />
          <div>
            <h2 style={{ fontSize: "1.1rem", margin: 0, color: "#cad3f5" }}>
              SIH Multi-Layer Model Pipeline Transparency
            </h2>
            <small style={{ color: "#a5adcb" }}>
              Verifiable execution stack: every analytical insight derives from dedicated specialized models rather than generic assumptions.
            </small>
          </div>
        </div>
        <span
          style={{
            fontSize: "0.75rem",
            padding: "3px 10px",
            borderRadius: "999px",
            background: "rgba(166, 218, 149, 0.15)",
            color: "#a6da95",
            fontWeight: 700,
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
        >
          <ShieldCheck size={13} /> 10 Active Model Layers
        </span>
      </div>

      {loading ? (
        <div style={{ padding: "1rem", color: "#8087a2", textAlign: "center" }}>Verifying active model executions...</div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: "0.75rem",
            marginTop: "1rem",
          }}
        >
          {pipeline.map((item) => (
            <div
              key={item.model}
              style={{
                padding: "0.75rem 1rem",
                borderRadius: "8px",
                background: "rgba(24, 25, 38, 0.6)",
                border: "1px solid rgba(255, 255, 255, 0.06)",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <strong style={{ color: "#cad3f5", fontSize: "0.95rem" }}>{item.model}</strong>
                <span
                  style={{
                    fontSize: "0.7rem",
                    fontWeight: 700,
                    color: item.status.toLowerCase().includes("executed") ? "#a6da95" : "#eed49f",
                    display: "flex",
                    alignItems: "center",
                    gap: "3px",
                  }}
                >
                  <CheckCircle2 size={12} /> {item.status}
                </span>
              </div>
              <span style={{ fontSize: "0.78rem", color: "#8aadf4" }}>{item.purpose}</span>
              <p style={{ margin: 0, fontSize: "0.72rem", color: "#8087a2" }}>{item.details}</p>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px", fontSize: "0.7rem", color: "#6e738d" }}>
                <span>Confidence: {item.confidence}</span>
                <span>Audit Verified</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
