"""
Bill Splitter
Handles the logic for splitting bills among multiple people
"""

from typing import Dict, List, Any


class BillSplitter:
    """
    Class to handle bill splitting logic.
    Calculates how much each person needs to pay based on item assignments.
    """
    
    def __init__(self):
        """Initialize the bill splitter"""
        self.people = []
        self.items = []
        self.assignments = {}
        self.additional_charges = []
        self.total = 0.0
    
    def set_people(self, people: List[str]) -> None:
        """
        Set the list of people participating in the bill split.
        
        Args:
            people: List of person names
        """
        self.people = people
    
    def set_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Set the list of items from the receipt.
        
        Args:
            items: List of item dictionaries with name, quantity, price, total
        """
        self.items = items
    
    def set_additional_charges(self, charges: List[Dict[str, float]]) -> None:
        """
        Set additional charges (tax, service, etc.).
        
        Args:
            charges: List of charge dictionaries with name and amount
        """
        self.additional_charges = charges
    
    def set_total(self, total: float) -> None:
        """
        Set the total bill amount.
        
        Args:
            total: Total bill amount
        """
        self.total = total
    
    def assign_item(self, item_index: int, person_names: List[str]) -> None:
        """
        Assign an item to one or more people.
        
        Args:
            item_index: Index of the item in the items list
            person_names: List of person names who will pay for this item
        """
        if item_index < 0 or item_index >= len(self.items):
            raise ValueError(f"Invalid item index: {item_index}")
        
        for name in person_names:
            if name not in self.people:
                raise ValueError(f"Person '{name}' not in people list")
        
        self.assignments[item_index] = person_names
    
    def calculate_split(self) -> Dict[str, Any]:
        """
        Calculate how much each person needs to pay.
        
        Returns:
            Dictionary with per-person breakdown:
            {
                "person_name": {
                    "items": [{"name": str, "amount": float}],
                    "subtotal": float,
                    "additional_charges": float,
                    "total": float
                }
            }
        """
        # Initialize result structure
        result = {person: {
            "items": [],
            "subtotal": 0.0,
            "additional_charges": 0.0,
            "total": 0.0
        } for person in self.people}
        
        # Calculate item costs per person
        for item_idx, item in enumerate(self.items):
            if item_idx in self.assignments:
                assigned_people = self.assignments[item_idx]
                num_people = len(assigned_people)
                
                if num_people > 0:
                    amount_per_person = item["total"] / num_people
                    
                    for person in assigned_people:
                        result[person]["items"].append({
                            "name": item["name"],
                            "amount": amount_per_person
                        })
                        result[person]["subtotal"] += amount_per_person
        
        # Calculate total subtotal from all people
        total_subtotal = sum(person_data["subtotal"] for person_data in result.values())
        
        # Distribute additional charges proportionally
        if total_subtotal > 0:
            total_charges = sum(charge["amount"] for charge in self.additional_charges)
            
            for person in self.people:
                person_subtotal = result[person]["subtotal"]
                proportion = person_subtotal / total_subtotal if total_subtotal > 0 else 0
                result[person]["additional_charges"] = total_charges * proportion
                result[person]["total"] = person_subtotal + result[person]["additional_charges"]
        
        return result
    
    def validate_split(self, split_result: Dict[str, Any], strict: bool = False) -> bool:
        """
        Validate that the split adds up to the total bill.
        
        Args:
            split_result: Result from calculate_split()
            strict: If True, require exact match. If False, allow reasonable difference.
            
        Returns:
            True if valid (sum equals total), False otherwise
        """
        calculated_total = sum(person_data["total"] for person_data in split_result.values())
        
        # Allow small floating point differences
        tolerance = 0.01 if strict else max(self.total * 0.1, 100)  # 10% or Rp 100
        
        # If all items are assigned, trust the calculated total
        all_items_assigned = all(
            idx in self.assignments and len(self.assignments[idx]) > 0 
            for idx in range(len(self.items))
        )
        
        if all_items_assigned and not strict:
            # If all items assigned, validation is based on item totals, not bill total
            return True
        
        return abs(calculated_total - self.total) < tolerance
    
    def get_summary(self, split_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of the bill split.
        
        Args:
            split_result: Result from calculate_split()
            
        Returns:
            Summary dictionary with totals and validation
        """
        calculated_total = sum(person_data["total"] for person_data in split_result.values())
        
        return {
            "num_people": len(self.people),
            "num_items": len(self.items),
            "bill_total": self.total,
            "calculated_total": calculated_total,
            "is_valid": self.validate_split(split_result),
            "difference": abs(calculated_total - self.total)
        }
