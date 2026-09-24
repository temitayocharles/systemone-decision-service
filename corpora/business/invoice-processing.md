# Invoice processing guide

## Overview

Acme Finance uses a standard invoice review flow. The purpose is to confirm the vendor, amount, account, and required approval for payment.

## Required checks

- Supplier is in the approved vendor list.
- Invoice matches the purchase order or contract terms.
- Amount is consistent with the expected billing period.
- Tax and currency codes are valid for the country and entity.

## Exceptions

Invoices without a matching PO, invoices that are over threshold, or invoices with missing tax information must be escalated to the approver queue for review.

## Decision guidance

The first question is whether the invoice matches an approved vendor and a valid purchase order. If not, do not approve payment until the exception is resolved.
