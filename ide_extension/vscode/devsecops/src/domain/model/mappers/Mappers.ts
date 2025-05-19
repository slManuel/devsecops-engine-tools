import { Finding } from "../Finding";

export interface IIacContextCheckov {
  id: string;
  custom_vuln_id: string;
  check_name: string;
  check_class: string;
  severity: string;
  where: string;
  resource: string;
  description: string;
  module: string;
  tool: string;
}

export interface IImageScanContextTrivy {
  id: string;
  cve_id: string;
  custom_vuln_id: string;
  check_name: string;
  check_class: string;
  severity: string;
  package_name: string;
  os_type: string;
  layer_digest: string;
  resource: string;
  description: string;
  module: string;
  source_tool: string;
  references: string[];
}

export class Mappers {
  public static mapIacContextCheckovToFinding(
    iacContextCheckov: IIacContextCheckov
  ): Finding {
    return new Finding(
      iacContextCheckov.id || "",
      iacContextCheckov.custom_vuln_id || iacContextCheckov.id || "",
      iacContextCheckov.check_name || "",
      iacContextCheckov.check_class || "",
      iacContextCheckov.severity || "unknown",
      iacContextCheckov.where || "",
      iacContextCheckov.resource || "",
      iacContextCheckov.description || "",
      iacContextCheckov.module || "engine_iac",
      iacContextCheckov.tool || "Checkov"
    );
  }

  public static mapImageScanContextTrivyToFinding(
    imageScanContextTrivy: IImageScanContextTrivy
  ): Finding {
    return new Finding(
      imageScanContextTrivy.id || imageScanContextTrivy.cve_id || "",
      imageScanContextTrivy.custom_vuln_id ||
        imageScanContextTrivy.id ||
        imageScanContextTrivy.cve_id ||
        "",
      imageScanContextTrivy.check_name || "",
      imageScanContextTrivy.check_class || "",
      imageScanContextTrivy.severity || "unknown",
      imageScanContextTrivy.package_name +
        " " +
        imageScanContextTrivy.os_type +
        ":" +
        imageScanContextTrivy.layer_digest || "",
      imageScanContextTrivy.resource || "",
      imageScanContextTrivy.description || "",
      imageScanContextTrivy.module || "engine_container",
      imageScanContextTrivy.source_tool || "Trivy",
      imageScanContextTrivy.references || []
    );
  }
}
