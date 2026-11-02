Safe to Send · Ep 17 — The newsletter that silently didn't send

Most campaign incidents I've handled weren't in the email. They were in the workflow behind it.

So I built a small workflow x-ray. It reads a workflow, builds the graph, and flags what will hurt you at 06:00 on a Monday:
→ queries, sends and scripts with no error branch (a failure alerts nobody)
→ a query with no filter (full recipient table scan)
→ a branch that never joins back, so the stats step never runs
→ dead ends and dead code

A synthetic weekly newsletter scored 0/100: 7 errors, 3 warnings. The fixed version scored 100. The fix was mostly adding one "alert on-call" step and drawing an error line to it from everything risky.

It also prints a Mermaid diagram with the error branches dotted, so the gap is visible to someone who has never opened the workflow.

What's the first thing you check in someone else's workflow?

Repo: https://github.com/sghatge/safe-to-send-17-workflow-xray

#SafeToSend #AdobeCampaign #Workflow #CRMOps
