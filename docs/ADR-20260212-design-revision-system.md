# ADR-20260212: Design Revision System

## Status
Accepted

## Context
For SEMI_PRIVATE and PRIVATE design plans, there was no structured way for designers to submit design iterations or for customers to review, approve, or request changes. The existing workflow jumped directly from DESIGNING to READY_FOR_PRINT without a feedback loop. Business rules require:

- Designers submit design files to customers for review.
- Customers can approve or reject designs with feedback.
- SEMI_PRIVATE plans have a limited number of revisions (`max_revisions` from `CategoryDesignPlan`); once exhausted, the design is auto-approved.
- PRIVATE plans have unlimited revisions and include a real-time chat channel between customer and designer.

## Decision
Introduce two new models and associated services:

1. **`DesignRevision`** table tracking each design version per order: version number, file URL, customer feedback, and status (PENDING_REVIEW / APPROVED / REJECTED). This provides a full audit trail of the design iteration process.

2. **`Message`** table for order-scoped chat between customer and assigned designer, available only for PRIVATE plans in DESIGNING status. Messages support text and optional file attachments.

3. **`DesignRevisionService`** and **`MessageService`** encapsulate all business logic (auto-approval, access control, read tracking) in the service layer, keeping routers thin.

4. **Designer router** (`/api/v1/designer/*`) with hybrid authentication (JWT + query param) to support both web frontend and bot clients.

## Why
- **Audit trail**: Every design iteration and customer feedback is permanently stored, avoiding disputes.
- **Auto-approval**: Prevents infinite revision loops on SEMI_PRIVATE plans by enforcing the contractual revision limit.
- **Separation of concerns**: Chat is only enabled for PRIVATE plans where direct communication is part of the service level, keeping SEMI_PRIVATE flow simpler.
- **Hybrid auth**: Reuses the same pattern as Print Shop endpoints, enabling bot integration without separate API.

## Impact
- Two new database tables: `design_revisions`, `messages`.
- New enum: `RevisionStatus` (PENDING_REVIEW, APPROVED, REJECTED).
- New column on `orders`: `design_plan_id` (FK to `category_design_plans`).
- New backend services: `DesignRevisionService`, `MessageService`.
- New API router: `/api/v1/designer/`.
- New customer endpoints: approve/reject design, chat messages.
- New frontend pages: Designer dashboard, order list, order detail with upload/chat.
- Customer order detail enhanced with design review section, revision history, and chat (PRIVATE).
