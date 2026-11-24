import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
type JsPDFWithAutoTable = jsPDF & {
  lastAutoTable: {
    finalY: number;
  };
};


interface IncidentAnalyticsReport {
  total_incidents: number;
  open_incidents: number;
  investigating_incidents: number;
  resolved_incidents: number;
  resolution_rate: number;
  severity_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
  daily_trend: { date: string; count: number }[];
  last_7_days_count: number;
  generated_at: string;
}

export function exportIncidentAnalyticsPDF(data: IncidentAnalyticsReport) {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();

  doc.setFontSize(20);
  doc.text("InfraSentry AI", 14, 20);

  doc.setFontSize(15);
  doc.text("Incident Analytics Report", 14, 31);

  doc.setFontSize(9);
  doc.text(
    `Generated: ${new Date(data.generated_at).toLocaleString()}`,
    14,
    39
  );

  autoTable(doc, {
    startY: 48,
    head: [["Metric", "Value"]],
    body: [
      ["Total Incidents", String(data.total_incidents)],
      ["Open Incidents", String(data.open_incidents)],
      ["Investigating Incidents", String(data.investigating_incidents)],
      ["Resolved Incidents", String(data.resolved_incidents)],
      ["Resolution Rate", `${data.resolution_rate}%`],
      ["Last 7 Days", String(data.last_7_days_count)],
    ],
    theme: "grid",
    headStyles: { fillColor: [30, 64, 120] },
  });

  let y = (doc as JsPDFWithAutoTable).lastAutoTable.finalY + 12;

  doc.setFontSize(13);
  doc.text("Severity Distribution", 14, y);

  autoTable(doc, {
    startY: y + 5,
    head: [["Severity", "Count"]],
    body: Object.entries(data.severity_distribution).map(
      ([severity, count]) => [severity, String(count)]
    ),
    theme: "striped",
  });

  y = (doc as JsPDFWithAutoTable).lastAutoTable.finalY + 12;

  if (y > 240) {
    doc.addPage();
    y = 20;
  }

  doc.setFontSize(13);
  doc.text("Status Distribution", 14, y);

  autoTable(doc, {
    startY: y + 5,
    head: [["Status", "Count"]],
    body: Object.entries(data.status_distribution).map(
      ([status, count]) => [status, String(count)]
    ),
    theme: "striped",
  });

  y = (doc as JsPDFWithAutoTable).lastAutoTable.finalY + 12;

  if (y > 240) {
    doc.addPage();
    y = 20;
  }

  doc.setFontSize(13);
  doc.text("7-Day Incident Trend", 14, y);

  autoTable(doc, {
    startY: y + 5,
    head: [["Date", "Incidents"]],
    body: data.daily_trend.map((item) => [
      item.date,
      String(item.count),
    ]),
    theme: "grid",
  });

  const pageCount = doc.getNumberOfPages();

  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.text(
      `InfraSentry AI | Page ${i} of ${pageCount}`,
      pageWidth / 2,
      290,
      { align: "center" }
    );
  }

  doc.save(`InfraSentry_Incident_Report_${Date.now()}.pdf`);
}
