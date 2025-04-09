# Contributing to A-List Home Pros Project

Thank you for your interest in contributing to the A-List Home Pros project! This guide explains the contribution process and task management in the project.

## Task Management

We use two main systems for task management and tracking:

### 1. GitHub Issues

We use GitHub Issues to track features, bugs, and improvements. When creating a new issue, please follow these guidelines:

- Use a clear and concise title
- Choose the appropriate category (bug, feature, enhancement, etc.)
- Provide a detailed description of the problem or feature
- Add appropriate labels for easier classification
- Specify priority if possible

#### GitHub Issues Labels

We use the following labels to organize tasks:

- `bug`: Problem or error in the code
- `feature`: New feature
- `enhancement`: Improvement to an existing feature
- `documentation`: Documentation improvements
- `frontend`: Tasks related to the front-end
- `backend`: Tasks related to the back-end
- `high-priority`: High priority tasks
- `low-priority`: Low priority tasks

### 2. Trello

In addition to GitHub Issues, we use Trello for strategic planning and daily task management. The Trello board is organized as follows:

- **Backlog**: Tasks planned for the future
- **To Do**: Tasks planned for the current cycle
- **In Progress**: Tasks currently being implemented
- **Review**: Tasks awaiting review
- **Done**: Completed tasks

To access the Trello board, please contact the project manager for an invitation.

## Contribution Process

### 1. Choosing a Task

1. Review GitHub Issues or the Trello board to find a suitable task
2. Assign the task to yourself or request assignment
3. Move the task to "In Progress" in Trello (if using Trello)

### 2. Working on the Task

1. Create a new branch from `main` using a clear naming convention:
   ```
   git checkout -b feature/feature-name
   ```
   or
   ```
   git checkout -b fix/fix-name
   ```

2. Implement the required changes
3. Make sure to follow the [Development Guidelines](README.md#📝-development-guidelines)
4. Add tests for new code if possible

### 3. Submitting Changes

1. Commit your changes with a descriptive message:
   ```
   git commit -m "Brief description of changes"
   ```

2. Push the changes to your branch:
   ```
   git push origin branch-name
   ```

3. Create a Pull Request on GitHub
4. Link the Pull Request to the related Issue using words like "Fixes #123" or "Resolves #123"
5. Wait for review and comments

### 4. Code Review

1. A team member will review the code
2. Make any required changes based on comments
3. Once the changes are approved, the code will be merged into the main branch

## General Guidelines

- Maintain regular communication about task progress
- Update task status in Trello or GitHub Issues
- Ask for help when needed
- Review other people's Pull Requests when possible
- Adhere to the code and documentation standards outlined in the [Development Guidelines](README.md#📝-development-guidelines)

Thank you for your contribution to the A-List Home Pros project!
