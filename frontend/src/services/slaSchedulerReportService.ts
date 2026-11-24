import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
type JsPDFWithAutoTable = jsPDF & {
  lastAutoTable: {
    finalY: number;
  };
};


export interface SchedulerReport {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  average_duration_ms: number;
  last_run: string | null;
  last_status: string;
  history: {
    timestamp: string;
    status: string;
    duration_ms: number;
    message?: string | null;
  }[];
  retained_history: number;
}

export function exportSchedulerCSV(data: SchedulerReport) {
  const successRate = data.total_runs
    ? ((data.successful_runs / data.total_runs) * 100).toFixed(2)
    : "0.00";

  const rows = [
    ["InfraSentry AI - SLA Scheduler Analytics"],
    ["Generated At", new Date().toISOString()],
    ["Total Executions", String(data.total_runs)],
    ["Successful Executions", String(data.successful_runs)],
    ["Failed Executions", String(data.failed_runs)],
    ["Success Rate (%)", successRate],
    ["Average Duration (ms)", String(data.average_duration_ms)],
    ["Last Status", data.last_status],
    [],
    ["Timestamp", "Status", "Duration (ms)", "Message"],
    ...data.history.map((item) => [
      item.timestamp,
      item.status,
      String(item.duration_ms),
      item.message || "",
    ]),
  ];

  const csvCell = (value: unknown): string => {
    let text = String(value ?? "");
    if (/^[=+\-@\t\r]/.test(text)) text = "'" + text;
    return `"${text.replace(/"/g, '""')}"`;
  };

  const csv = rows
    .map((row) => row.map(csvCell).join(","))
    .join("\r\n");

  const blob = new Blob(["\uFEFF", csv], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `infrasentry_sla_scheduler_${Date.now()}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

export function exportSchedulerPDF(data: SchedulerReport) {
  const doc = new jsPDF();
  const successRate = data.total_runs
    ? ((data.successful_runs / data.total_runs) * 100).toFixed(2)
    : "0.00";

  doc.setFontSize(18);
  doc.text("InfraSentry AI", 14, 18);

  doc.setFontSize(13);
  doc.text("SLA Scheduler Performance Report", 14, 27);

  doc.setFontSize(9);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 35);

  autoTable(doc, {
    startY: 43,
    head: [["Metric", "Value"]],
    body: [
      ["Total Executions", String(data.total_runs)],
      ["Successful Executions", String(data.successful_runs)],
      ["Failed Executions", String(data.failed_runs)],
      ["Success Rate", `${successRate}%`],
      ["Average Duration", `${data.average_duration_ms} ms`],
      ["Last Status", data.last_status],
      ["Last Run", data.last_run || "No execution recorded"],
    ],
    theme: "grid",
    styles: { fontSize: 9 },
  });

  autoTable(doc, {
    startY: (doc as JsPDFWithAutoTable).lastAutoTable.finalY + 12,
    head: [["Timestamp", "Status", "Duration (ms)", "Message"]],
    body: data.history.map((item) => [
      new Date(item.timestamp).toLocaleString(),
      item.status,
      String(item.duration_ms),
      item.message || "-",
    ]),
    theme: "striped",
    styles: { fontSize: 7, cellPadding: 2 },
    columnStyles: {
      0: { cellWidth: 48 },
      1: { cellWidth: 22 },
      2: { cellWidth: 25 },
      3: { cellWidth: "auto" },
    },
  });

  const pageCount = doc.getNumberOfPages();
  for (let page = 1; page <= pageCount; page++) {
    doc.setPage(page);
    doc.setFontSize(8);
    doc.text(
      `Page ${page} of ${pageCount}`,
      196,
      287,
      { align: "right" }
    );
  }

  doc.save(`infrasentry_sla_scheduler_${Date.now()}.pdf`);
}
