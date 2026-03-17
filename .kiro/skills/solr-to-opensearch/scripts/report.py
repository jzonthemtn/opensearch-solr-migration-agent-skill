from typing import List, Dict, Any

class MigrationReport:
    """Generates a migration report from session context."""

    def __init__(self, milestones: List[str] = None, blockers: List[str] = None, implementation_points: List[str] = None, cost_estimates: Dict[str, str] = None):
        self.milestones = milestones or []
        self.blockers = blockers or []
        self.implementation_points = implementation_points or []
        self.cost_estimates = cost_estimates or {}

    def generate(self) -> str:
        report = []
        report.append("# Solr to OpenSearch Migration Report\n")
        
        report.append("## Major Milestones")
        for i, m in enumerate(self.milestones, 1):
            report.append(f"{i}. {m}")
        report.append("")

        report.append("## Potential Blockers")
        for b in self.blockers:
            report.append(f"- {b}")
        if not self.blockers:
            report.append("- No immediate blockers identified.")
        report.append("")

        report.append("## Implementation Points")
        for ip in self.implementation_points:
            report.append(f"- {ip}")
        report.append("")

        report.append("## Cost Estimates")
        for item, est in self.cost_estimates.items():
            report.append(f"- **{item}**: {est}")
        if not self.cost_estimates:
            report.append("- TBD based on further infra analysis.")
        
        return "\n".join(report)
