"""
Cost Tracking Utilities

Track and analyze API usage costs across all services.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import csv

logger = logging.getLogger(__name__)


@dataclass
class CostEntry:
    """Single cost entry"""
    timestamp: str
    service: str  # groq, fal, elevenlabs
    operation: str  # story, image, video, voice
    cost: float
    details: str


class CostTracker:
    """
    Track and analyze API costs
    
    Features:
    - Per-service cost tracking
    - Daily/monthly aggregation
    - Budget alerts
    - CSV export
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize cost tracker
        
        Args:
            storage_path: Path to store cost data (JSON)
        """
        if storage_path is None:
            storage_path = Path("commercial/.temp/cost_history.json")
        
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.entries: List[CostEntry] = []
        self._load_history()
        
        logger.info(f"Initialized CostTracker (storage: {storage_path})")
    
    def log_cost(
        self,
        service: str,
        operation: str,
        cost: float,
        details: str = ""
    ):
        """
        Log a cost entry
        
        Args:
            service: Service name (groq, fal, elevenlabs)
            operation: Operation type (story, image, video, voice)
            cost: Cost in USD
            details: Additional details
        """
        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            service=service,
            operation=operation,
            cost=cost,
            details=details
        )
        
        self.entries.append(entry)
        self._save_history()
        
        logger.debug(f"Logged cost: {service}/{operation} = ${cost:.4f}")
    
    def get_total_cost(
        self,
        service: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> float:
        """
        Get total cost
        
        Args:
            service: Filter by service (None = all)
            since: Filter by date (None = all time)
            
        Returns:
            Total cost in USD
        """
        filtered = self.entries
        
        if service:
            filtered = [e for e in filtered if e.service == service]
        
        if since:
            filtered = [
                e for e in filtered
                if datetime.fromisoformat(e.timestamp) >= since
            ]
        
        return sum(e.cost for e in filtered)
    
    def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """Get cost for a specific day"""
        if date is None:
            date = datetime.now()
        
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        daily = [
            e for e in self.entries
            if start <= datetime.fromisoformat(e.timestamp) < end
        ]
        
        return sum(e.cost for e in daily)
    
    def get_monthly_cost(self, year: int, month: int) -> float:
        """Get cost for a specific month"""
        start = datetime(year, month, 1)
        
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        
        monthly = [
            e for e in self.entries
            if start <= datetime.fromisoformat(e.timestamp) < end
        ]
        
        return sum(e.cost for e in monthly)
    
    def get_breakdown(self, since: Optional[datetime] = None) -> Dict[str, float]:
        """
        Get cost breakdown by service
        
        Returns:
            Dictionary of {service: cost}
        """
        filtered = self.entries
        
        if since:
            filtered = [
                e for e in filtered
                if datetime.fromisoformat(e.timestamp) >= since
            ]
        
        breakdown = {}
        for entry in filtered:
            if entry.service not in breakdown:
                breakdown[entry.service] = 0.0
            breakdown[entry.service] += entry.cost
        
        return breakdown
    
    def check_budget(
        self,
        monthly_budget: float,
        alert_threshold: float = 0.8
    ) -> Dict:
        """
        Check if approaching budget limit
        
        Args:
            monthly_budget: Monthly budget in USD
            alert_threshold: Alert when usage exceeds this fraction
            
        Returns:
            Dictionary with budget status
        """
        now = datetime.now()
        monthly_cost = self.get_monthly_cost(now.year, now.month)
        
        usage_percent = monthly_cost / monthly_budget
        
        status = {
            "monthly_cost": monthly_cost,
            "monthly_budget": monthly_budget,
            "usage_percent": usage_percent,
            "remaining": monthly_budget - monthly_cost,
            "alert": usage_percent >= alert_threshold
        }
        
        if status["alert"]:
            logger.warning(
                f"⚠️ Budget alert: {usage_percent*100:.1f}% used "
                f"(${monthly_cost:.2f}/${monthly_budget:.2f})"
            )
        
        return status
    
    def export_csv(self, output_path: Path):
        """Export cost history to CSV"""
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['timestamp', 'service', 'operation', 'cost', 'details']
            )
            writer.writeheader()
            
            for entry in self.entries:
                writer.writerow(asdict(entry))
        
        logger.info(f"✅ Exported {len(self.entries)} entries to {output_path}")
    
    def _load_history(self):
        """Load cost history from storage"""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.entries = [CostEntry(**e) for e in data]
            
            logger.debug(f"Loaded {len(self.entries)} cost entries")
        except Exception as e:
            logger.error(f"Failed to load cost history: {e}")
    
    def _save_history(self):
        """Save cost history to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                data = [asdict(e) for e in self.entries]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cost history: {e}")


# Example usage
if __name__ == "__main__":
    tracker = CostTracker()
    
    # Log some costs
    tracker.log_cost("groq", "story", 0.002, "5 scenes")
    tracker.log_cost("fal", "image", 0.15, "5 images @ 28 steps")
    tracker.log_cost("fal", "video", 0.50, "5 videos @ 5s")
    tracker.log_cost("elevenlabs", "voice", 0.15, "500 characters")
    
    # Get totals
    print(f"Total cost: ${tracker.get_total_cost():.2f}")
    print(f"Today: ${tracker.get_daily_cost():.2f}")
    
    # Get breakdown
    breakdown = tracker.get_breakdown()
    print("\nBreakdown:")
    for service, cost in breakdown.items():
        print(f"  {service}: ${cost:.2f}")
    
    # Check budget
    status = tracker.check_budget(monthly_budget=100.0)
    print(f"\nBudget: {status['usage_percent']*100:.1f}% used")
    
    # Export
    tracker.export_csv(Path("cost_report.csv"))
