import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
type JsPDFWithAutoTable = jsPDF & {
  lastAutoTable: {
    finalY: number;
  };
};


export interface RetryReportRun {
  timestamp: string;
  status: string;
  attempts: number;
  duration_seconds: number;
  error: string | null;
}

export interface RetryReportMetrics {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  total_attempts: number;
  average_duration_seconds: number;
  last_run: RetryReportRun | null;
  history: RetryReportRun[];
}

function csvEscape(value: unknown): string {
  let text = String(value ?? "");
  if (/^[=+\-@\t\r]/.test(text)) text = "'" + text;
  return `"${text.replace(/"/g, '""')}"`;
}

export function exportRetryMetricsCSV(data: RetryReportMetrics): void {
  const rows = [
    ["Metric", "Value"],
    ["Total Runs", data.total_runs],
    ["Successful Runs", data.successful_runs],
    ["Failed Runs", data.failed_runs],
    ["Total Attempts", data.total_attempts],
    ["Average Duration (seconds)", data.average_duration_seconds],
    [],
    ["Timestamp", "Status", "Attempts", "Duration (seconds)", "Error"],
    ...data.history.map((run) => [
      run.timestamp,
      run.status,
      run.attempts,
      run.duration_seconds,
      run.error ?? "",
    ]),
  ];

  const csv = "\uFEFF" + rows
    .map((row) => row.map(csvEscape).join(","))
    .join("\r\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = "sla-retry-metrics.csv";
  anchor.click();

  URL.revokeObjectURL(url);
}

export function exportRetryMetricsPDF(data: RetryReportMetrics): void {
  const pdf = new jsPDF();

  pdf.setFontSize(18);
  pdf.text("SLA Retry Execution Report", 14, 18);

  pdf.setFontSize(10);
  pdf.text(`Generated: ${new Date().toLocaleString()}`, 14, 26);

  autoTable(pdf, {
    startY: 34,
    head: [["Metric", "Value"]],
    body: [
      ["Total Runs", String(data.total_runs)],
      ["Successful Runs", String(data.successful_runs)],
      ["Failed Runs", String(data.failed_runs)],
      ["Total Attempts", String(data.total_attempts)],
      ["Average Duration", `${data.average_duration_seconds.toFixed(2)} seconds`],
    ],
  });

  autoTable(pdf, {
    startY: (pdf as JsPDFWithAutoTable).lastAutoTable.finalY + 12,
    head: [["Timestamp", "Status", "Attempts", "Duration", "Error"]],
    body: data.history.map((run) => [
      run.timestamp,
      run.status,
      String(run.attempts),
      `${run.duration_seconds.toFixed(2)}s`,
      run.error ?? "-",
    ]),
    styles: { fontSize: 7, cellPadding: 2 },
    columnStyles: { 0: { cellWidth: 42 }, 4: { cellWidth: 45 } },
  });

  const pageCount = pdf.getNumberOfPages();
  for (let page = 1; page <= pageCount; page += 1) {
    pdf.setPage(page);
    pdf.setFontSize(8);
    pdf.text(
      `Page ${page} of ${pageCount}`,
      190,
      290,
      { align: "right" }
    );
  }

  pdf.save("sla-retry-metrics.pdf");
}
