# ADR-20260104: Dynamic Product Catalog System

## Status
Accepted

## Context
The initial system had a static product model where products were pre-defined with fixed attributes. Business requirements evolved to need:
- Admin-configurable product categories (labels, invoices, etc.)
- Dynamic attributes per category (size, material, etc.)
- Multiple design plans with different features per category
- Template gallery for public plans with logo placeholder
- Questionnaire system for semi-private plans

## Decision
Implement a dynamic catalog system with the following hierarchy:

```
Category (e.g., "Label")
├── CategoryAttribute (e.g., "Size", "Material")
│   └── AttributeOption (e.g., "5x5cm", "10x10cm")
├── CategoryDesignPlan (e.g., "Public", "Semi-Private")
│   ├── DesignTemplate (for public plans)
│   │   └── Placeholder info (x, y, width, height)
│   └── QuestionSection (for semi-private)
│       └── DesignQuestion
│           └── QuestionOption
└── OrderStepTemplate (workflow steps)
```

Key design decisions:
1. **Soft hierarchy**: Categories are independent, no parent-child relationship
2. **Conditional questions**: Questions can depend on previous answers
3. **Pillow for image processing**: Auto-place logos in template placeholders
4. **JSON validation rules**: Flexible validation per question type

## Alternatives Considered
1. **Hardcoded product types**: Less flexible, requires code changes
2. **EAV (Entity-Attribute-Value)**: More flexible but complex queries
3. **Document-based (MongoDB)**: Overkill, PostgreSQL JSONB sufficient

## Consequences
**Pros:**
- Admin can create new product types without code changes
- Flexible questionnaire system with conditional logic
- Template system reduces designer workload for public plans

**Cons:**
- More complex data model
- Requires careful UI/UX for admin management
- Template placeholder positioning requires design knowledge

## Impact on Future
- New product types can be added via admin panel
- Questionnaire system can be extended for other use cases
- Template system can support more placeholder types (text, QR codes)

