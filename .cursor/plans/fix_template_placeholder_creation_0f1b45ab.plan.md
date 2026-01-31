---
name: Fix Template Placeholder Creation
overview: ""
todos:
  - id: fix-placeholder-fields
    content: Fix placeholder creation to use 'name' and 'label_fa' fields instead of 'label'
    status: completed
  - id: improve-transparency
    content: Reduce placeholder background opacity for better template visibility
    status: completed
---

# Fix Template Placeholder Creation and Transparency

## Problem Analysis

1. **Field Mismatch Error**: When creating a template with placeholders, the frontend sends `label` field but the backend expects `name` (required) and `label_fa` (required) in `PlaceholderCreate` schema.
2. **Transparency**: Placeholder overlays should show the template image behind them. Currently they use semi-transparent colors but we need to ensure they are visible without obscuring the template.

## Changes Required

### 1. Fix Placeholder Creation in Catalog Page

File: [`frontend/src/app/(dashboard)/admin/catalog/page.tsx`](frontend/src/app/\\(dashboard)/admin/catalog/page.tsx)**Current code (line ~1507-1537)**:

```typescript
adminApi.createPlaceholder(newTemplate.id, {
  type: "IMAGE",
  label: `تصویر ${i + 1}`,  // WRONG: using 'label' instead of 'name' and 'label_fa'
  ...
})
```

**Fix**: Change `label` to `name` and `label_fa`:

```typescript
adminApi.createPlaceholder(newTemplate.id, {
  type: "IMAGE",
  name: `image_${i + 1}`,        // Technical name (slug-style)
  label_fa: `تصویر ${i + 1}`,   // Persian display label
  ...
})
```

Same fix for TEXT placeholders:

```typescript
adminApi.createPlaceholder(newTemplate.id, {
  type: "TEXT",
  name: `text_${i + 1}`,         // Technical name
  label_fa: `متن ${i + 1}`,     // Persian display label
  ...
})
```



### 2. Improve Placeholder Transparency (Optional Enhancement)

File: [`frontend/src/components/template-editor/TemplateCanvas.tsx`](frontend/src/components/template-editor/TemplateCanvas.tsx)Change placeholder background opacity from 20%/30% to more transparent 10%/20%:

```typescript
const baseColors = {
  IMAGE: {
    bg: isSelected ? "bg-blue-500/20" : "bg-blue-500/10",  // Reduced opacity
    border: isSelected ? "border-blue-500" : "border-blue-400/70",
    text: "text-blue-600",
  },
  TEXT: {
    bg: isSelected ? "bg-green-500/20" : "bg-green-500/10",
    border: isSelected ? "border-green-500" : "border-green-400/70",
    text: "text-green-600",
  },
};
```



## Summary

| Issue | Fix ||-------|-----|| `name: Field required` error | Add `name` field with English slug |