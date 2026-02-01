# DESIGN.md

Design Principles & Anti-Goals

## Purpose

This document defines the **design philosophy** of this library.

It exists to:

* Prevent accidental over-engineering
* Keep APIs stable and predictable
* Serve as a guardrail for AI-assisted development

---

## Goals

* Provide **small, composable utilities** for Azure Functions
* Favor **explicit behavior over implicit magic**
* Keep runtime overhead minimal
* Remain easy to understand, debug, and remove

---

## Anti-Goals

This library intentionally does **NOT** aim to:

* Be a framework
* Hide or abstract Azure Functions runtime behavior
* Manage deployment, infrastructure, or configuration
* Introduce global state or hidden side effects

---

## API Design Principles

* Explicit is better than implicit
* No global mutable state
* Context must be **passed explicitly**, never inferred
* Public APIs are stable and conservative
* Breaking changes are avoided unless strictly necessary

---

## Compatibility Policy

* Minimum supported Python version: **3.10**
* Public APIs follow **Semantic Versioning**
* Experimental APIs may change without notice

---

## Experimental APIs

* Experimental APIs must be clearly documented
* Experimental APIs are **not protected by SemVer guarantees**
* Promotion from experimental → stable is explicit and intentional

Experimental APIs must be labeled in docs with **(Experimental)**.
