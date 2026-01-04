# ADR-20260104: Card-to-Card Payment Flow

## Status
Accepted

## Context
For the Iranian market, online payment gateways (PSP) have limitations:
- High transaction fees
- Complex integration
- Some businesses prefer manual verification

Many small businesses prefer card-to-card payments where:
1. Customer sees the business card number
2. Customer transfers money via their banking app
3. Customer uploads receipt image
4. Admin manually verifies and approves

## Decision
Implement a card-to-card payment flow with the following states:

```
PENDING ──(upload receipt)──> AWAITING_APPROVAL ──(approve)──> SUCCESS
                                    │
                                    └──(reject)──> FAILED
                                                     │
                                                     └──(re-upload)──> AWAITING_APPROVAL
```

Components:
1. **SystemSettings**: Store payment card info (card number, holder name)
2. **Payment model**: Extended with `receipt_image_url`, `approved_by`, `rejection_reason`
3. **Admin notification**: Alert admins when receipt is uploaded
4. **Approval flow**: Admin reviews receipt and approves/rejects

API Endpoints:
- `GET /settings/payment-card` - Customer gets card info
- `POST /payments/{id}/upload-receipt` - Customer uploads receipt
- `GET /payments/pending-approval` - Admin gets pending list
- `POST /payments/{id}/approve` - Admin approves
- `POST /payments/{id}/reject` - Admin rejects with reason

## Alternatives Considered
1. **PSP Integration only**: Limited by gateway availability
2. **Cryptocurrency**: Not suitable for target market
3. **Cash on delivery**: Increases logistics complexity

## Consequences
**Pros:**
- No PSP fees or integration complexity
- Manual verification provides fraud protection
- Familiar workflow for Iranian customers

**Cons:**
- Manual admin work for each payment
- Potential for human error in verification
- Slower than automated payment

## Security Considerations
- Receipt images stored securely (not publicly accessible)
- Admin-only access to approval endpoints
- Audit trail via logging (`payment.approved`, `payment.rejected`)

## Impact on Future
- Can add PSP integration as alternative payment method
- Admin workload can be reduced with OCR receipt verification
- Multiple admins can share approval workload

