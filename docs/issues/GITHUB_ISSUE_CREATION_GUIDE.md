# GitHub Issue Creation Guide

이 가이드는 `docs/issues/` 디렉토리의 문서들을 사용하여 GitHub 이슈를 생성하는 방법을 설명합니다.

This guide explains how to create GitHub issues from the documents in `docs/issues/` directory.

## 🎯 Quick Start

### Method 1: Copy & Paste (Recommended)
1. Open issue document (e.g., `01-cache-falsy-value-bug.md`)
2. Copy the entire markdown content
3. Go to GitHub → Issues → New Issue
4. Paste the content
5. Add labels (see below)
6. Click "Submit new issue"

### Method 2: Use GitHub CLI
```bash
# Install GitHub CLI if not already installed
# brew install gh  # macOS
# sudo apt install gh  # Ubuntu

# Authenticate
gh auth login

# Create issue from file
gh issue create \
  --title "Fix Cache Logic Bug - Falsy Value Handling" \
  --body-file docs/issues/01-cache-falsy-value-bug.md \
  --label "bug,critical,caching" \
  --assignee "@me"
```

### Method 3: Automated Script
Use the script below to create all issues at once.

## 📝 Issue Creation Template

For each issue, use this process:

1. **Title**: Use the H1 heading from the document (without "Issue #X:")
2. **Body**: Copy the entire markdown content
3. **Labels**: Add labels based on the "Labels" section in each document
4. **Assignee**: Assign to appropriate team member
5. **Milestone**: Assign to phase milestone (optional)
6. **Project**: Add to project board (optional)

## 🏷️ Label Mapping

### Priority Labels
| Document Priority | GitHub Label | Color |
|-------------------|--------------|-------|
| 🔴 CRITICAL | `critical` | #d73a4a (red) |
| 🟠 HIGH | `high-priority` | #ff9800 (orange) |
| 🟡 MEDIUM | `medium-priority` | #ffd700 (yellow) |
| 🟢 LOW | `low-priority` | #90ee90 (green) |

### Type Labels
| Category | GitHub Label | Color |
|----------|--------------|-------|
| Bug Fix | `bug` | #d73a4a (red) |
| Security | `security` | #e4003a (dark red) |
| Code Quality | `refactoring` | #fbca04 (yellow) |
| Performance | `performance` | #9c27b0 (purple) |
| Monitoring | `observability` | #0366d6 (blue) |

### Additional Labels
- `good-first-issue` - For issues suitable for new contributors
- `quick-fix` - For issues that can be fixed in < 1 hour
- `breaking-change` - For changes that break backward compatibility
- `enhancement` - For new features or improvements

## 🚀 Batch Creation Script

Save this as `create_issues.sh`:

```bash
#!/bin/bash

# Array of issue files and their metadata
# Format: "filename|title|labels"
declare -a issues=(
  "01-cache-falsy-value-bug.md|Fix Cache Logic Bug - Falsy Value Handling|bug,critical,caching,good-first-issue"
  "02-missing-return-in-decorator.md|Fix Missing Return Statement in monitor_performance Decorator|bug,critical,monitoring,quick-fix"
  "03-thread-safety-serverinfo.md|Add Thread-Safety to ServerInfo Counter Operations|bug,critical,concurrency,thread-safety"
  "04-html-sanitization-improvement.md|Improve HTML Sanitization in Swagger UI|security,high-priority,xss-prevention,swagger-ui"
  "05-url-sanitization-bypass.md|Fix URL Sanitization Bypass Risk|security,high-priority,xss-prevention,ssrf-prevention"
  "06-route-validation-spaces.md|Remove Spaces from Route Validation Pattern|security,input-validation,medium-priority,routes"
  "07-error-handling-schema-generation.md|Improve Error Handling in OpenAPI Schema Generation|enhancement,error-handling,medium-priority,observability"
  "08-cli-code-duplication.md|Refactor CLI Output Formatting Code Duplication|refactoring,code-quality,cli,medium-priority"
  "09-cli-type-validation.md|Add Input Type Validation in validate_openapi_spec|bug-prevention,input-validation,cli,medium-priority"
  "10-cache-key-performance.md|Optimize Cache Key Generation Performance|performance,caching,enhancement,low-priority"
  "11-cache-statistics.md|Add Cache Hit/Miss Statistics|enhancement,observability,caching,monitoring,low-priority"
  "12-deque-response-times.md|Replace List with Deque for Response Time Storage|performance,optimization,monitoring,low-priority"
  "13-median-calculation.md|Use statistics.median() for Accurate Median Calculation|correctness,monitoring,low-priority,quick-fix"
  "14-response-time-placeholder.md|Replace Placeholder Response Time Estimation with Real Metrics|enhancement,monitoring,integration,medium-priority"
)

# Base directory for issue files
ISSUES_DIR="docs/issues"

# Create issues
for issue in "${issues[@]}"; do
  IFS='|' read -r filename title labels <<< "$issue"
  
  echo "Creating issue: $title"
  
  gh issue create \
    --title "$title" \
    --body-file "$ISSUES_DIR/$filename" \
    --label "$labels"
  
  if [ $? -eq 0 ]; then
    echo "✓ Created: $title"
  else
    echo "✗ Failed: $title"
  fi
  
  # Small delay to avoid rate limiting
  sleep 2
done

echo ""
echo "All issues created!"
```

### Usage:
```bash
chmod +x create_issues.sh
./create_issues.sh
```

## 📋 Manual Creation Checklist

For each issue, check:
- [ ] Title is clear and descriptive
- [ ] All content from markdown file is included
- [ ] Priority label added
- [ ] Type label added
- [ ] Additional labels added (good-first-issue, quick-fix, etc.)
- [ ] Assigned to appropriate team member (if known)
- [ ] Added to milestone (if using milestones)
- [ ] Added to project board (if using projects)

## 🎨 Recommended Issue Organization

### Milestones
Create these milestones in your repository:

1. **v1.1.0 - Critical Fixes**
   - Issues: #1, #2, #3
   - Due date: ASAP
   
2. **v1.2.0 - Security Hardening**
   - Issues: #4, #5
   - Due date: Next sprint
   
3. **v1.3.0 - Code Quality**
   - Issues: #6, #7, #8, #9, #14
   - Due date: 2-3 sprints
   
4. **v1.4.0 - Performance & Monitoring**
   - Issues: #10, #11, #12, #13
   - Due date: Future

### Project Board Columns
1. 📋 **Backlog** - All new issues
2. 🎯 **Ready** - Prioritized and ready to start
3. 🚧 **In Progress** - Currently being worked on
4. 👀 **In Review** - PR submitted, awaiting review
5. ✅ **Done** - Merged and closed

## 🔗 Issue References

When creating issues, you can reference related issues:

```markdown
## Related Issues
- Blocks #2 (this issue must be fixed first)
- Blocked by #1 (wait for this to be fixed)
- Related to #4 (similar security concern)
- Depends on #3 (needs thread-safety first)
```

## 📊 Progress Tracking

After creating issues, you can track progress:

```bash
# View all issues
gh issue list

# View issues by label
gh issue list --label "critical"
gh issue list --label "good-first-issue"

# View issues by milestone
gh issue list --milestone "v1.1.0 - Critical Fixes"

# View issue status
gh issue view 1
```

## 💡 Tips

1. **Start with Critical Issues**: Create issues #1, #2, #3 first
2. **Add Context**: Include additional context if needed in the issue
3. **Tag People**: Use @mentions to notify relevant people
4. **Link PRs**: When creating PRs, reference the issue number (Fixes #1)
5. **Update Status**: Move issues through project board as they progress
6. **Close When Done**: Close issues when PR is merged and changes are verified

## 🆘 Common Problems

### Issue Not Created
- Check if you have permission to create issues
- Verify GitHub CLI is authenticated: `gh auth status`
- Check rate limits: wait a few minutes and try again

### Labels Not Found
- Create labels first in repository settings
- Use exact label names from the mapping above
- Labels are case-sensitive

### File Not Found
- Verify you're in the repository root directory
- Check file path: `docs/issues/01-cache-falsy-value-bug.md`
- Use absolute paths if needed

## 📞 Need Help?

If you encounter issues:
1. Check GitHub documentation: https://docs.github.com/issues
2. Check GitHub CLI docs: https://cli.github.com/manual/gh_issue_create
3. Ask in team chat or create a discussion

---

**Ready to start?** Begin with the critical issues and work your way through!
