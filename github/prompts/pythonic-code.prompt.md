# 🧩 Reusable Prompt — “Make This Code More Pythonic”

Use this prompt inside VS Code (Copilot Chat, Claude Code, or any LLM tool) to refactor existing Python code into **idiomatic, clean, expressive Pythonic code**, following community best practices.

---

## 🎯 Purpose

Transform the selected or referenced Python code into a version that reflects Pythonic design principles — focusing on clarity, simplicity, readability, and use of idiomatic syntax.

---

## 🐍 Prompt

You are a **Pythonic code refactoring expert**.  
Analyze the given Python code and refactor it so that it fully aligns with **Pythonic principles** and modern idioms.  
Ensure the result is clear, concise, expressive, and easy to maintain.

Apply the following structured checklist:

---

### I. General Philosophy and Structure
- Favor **simplicity and readability** over cleverness.  
- Use **idiomatic syntax** that feels natural in Python.  
- Emphasize **expressiveness** through built-ins, comprehensions, and generators.  
- Avoid unnecessary abstraction or overengineering.  
- Prefer solutions that are **easy to reason about**.  
- Use and leverage Python’s **standard library** effectively.

---

### II. Code Organization and Entry Points
- Prefer **functions** over classes when state is not required.  
- Define a clear entry point:  
```python
  if __name__ == "__main__":
      main()
```

* Centralize constants and configuration at the top of the file.
* Use **`pathlib.Path`** for all file and directory handling.

---

### III. Data Management and Typing

* Add **type annotations** for all functions and return values.
* Use **`@dataclass`** for structured data models.
* Use `field(default_factory=...)` for dynamic defaults (e.g., timestamps).
* Keep data handling explicit and predictable.

---

### IV. Flow Control and Resource Management

* Use **context managers** (`with` blocks) to handle resources.
* Follow **EAFP (Easier to Ask Forgiveness than Permission)** — handle exceptions instead of pre-checks.
* Use **iterators/generators** (`yield`) for streaming data.
* Prefer **comprehensions** over verbose loops when appropriate.
* Replace `print()` debugging with the **`logging`** module.

---

### Output Format

Return only the **rewritten Python code**, clean and ready to use.
Include concise comments if needed to clarify significant refactors.

---

### Example Usage

> “Refactor the following script to be fully Pythonic using the checklist above.”
> *(Paste code block here)*

---

**Goal:** Produce production-quality Python code that looks like it was written by an experienced Python developer who follows PEP 8, PEP 20, and standard library idioms.
