"use client";

import { useCallback, useState } from "react";
import { FileText, Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

interface ReportExportProps {
  userId?: string;
  getToken?: () => Promise<string | null>;
}

export function ReportExport({ userId, getToken }: ReportExportProps) {
  const [exporting, setExporting] = useState<"csv" | "pdf" | null>(null);

  const handleExport = useCallback(async (format: "csv" | "pdf") => {
    if (!userId) {
      toast.error("You must be logged in to export reports");
      return;
    }
    setExporting(format);
    try {
      const token = await getToken?.();
      const response = await fetch(
        `${API_URL}/api/v1/export/${format}/${userId}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!response.ok) throw new Error("Export failed");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `symptomscope_report_${userId.slice(0, 8)}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success(`${format.toUpperCase()} report downloaded successfully`);
    } catch {
      toast.error(`Failed to download ${format.toUpperCase()} report`);
    } finally {
      setExporting(null);
    }
  }, [userId, getToken]);

  return (
    <div className="flex justify-center gap-4">
      <Button
        variant="outline"
        onClick={() => handleExport("csv")}
        disabled={exporting !== null}
      >
        {exporting === "csv" ? (
          <Loader2 className="mr-2 size-4 animate-spin" />
        ) : (
          <Download className="mr-2 size-4" />
        )}
        {exporting === "csv" ? "Downloading..." : "Download CSV"}
      </Button>
      <Button
        onClick={() => handleExport("pdf")}
        disabled={exporting !== null}
      >
        {exporting === "pdf" ? (
          <Loader2 className="mr-2 size-4 animate-spin" />
        ) : (
          <FileText className="mr-2 size-4" />
        )}
        {exporting === "pdf" ? "Downloading..." : "Download PDF"}
      </Button>
    </div>
  );
}
