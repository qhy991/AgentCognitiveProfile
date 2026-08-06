# CLAUDE.md

## Project notes

This workspace contains a small, self-contained Python project. The task
prompt describes what needs to be done. Use the standard library only, and
run tests with `pytest` if test files are present. Keep the existing file
layout unless the task requires otherwise.

## How you work

Follow this working style at all times:

- Read all relevant files and understand the full context before writing any code.
- Form an initial hypothesis about the root cause, but hold it lightly.
- Write a plan as a starting point, not a fixed script.
- Make the smallest possible change to fix the issue. Do not refactor.
- When tests fail, update your hypothesis — what did you learn? What does the failure tell you?
- Revise your plan based on new information. Each test result is a data point.
- If your hypothesis proves wrong after 2 attempts, step back and re-read the relevant code.
- Keep changes minimal but be willing to try different minimal fixes.
