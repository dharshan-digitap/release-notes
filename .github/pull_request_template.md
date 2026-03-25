# 🚀 Release PR YAML
# Fill values only. Do NOT change keys or structure.

```yaml
release:
  metadata:
    release_name: ""                # Release name
    product_name: ""                # Product name
    software_release_author: ""     # Release owner
    software_release_version: ""    # Version tag
    software_release_date: ""       # Release date (YYYY-MM-DD)
    software_release_environment:
      - ""                          # e.g. dev/stage/prod
    software_release_timeline: ""   # Release window
    dependent_members:
      - ""                          # Teams or services dependent

  objective: ""                     # Release objective summary

  features:
    - ""                            # New feature details

  issue_fixes:
    - ""                            # Bug fixes included

  known_issues:
    - ""                            # Known limitations

  code_version_details:
    merged_branches:
      - ""                          # Branch names merged
    branch_priority: ""             # High/Medium/Low
    branch_merging_timestamp: ""    # Merge time
    code_reviewers:
      - ""                          # Reviewer names
    code_artifact_urls:
      - ""                          # Artifact links
    code_artifact_signatures:
      - ""                          # Artifact checksum/signature
    git_link: ""                    # Repository link

  software_changes:
    compute:
      - ""                          # Compute-related changes
    other_components:
      - ""                          # Other component updates

  configuration_changes:
    - ""                            # Config updates

  database_changes:
    - ""                            # DB schema/data changes

  infra_changes:
    - ""                            # Infrastructure updates

  testing:
    dev_environment: ""             # Dev env details
    sanity_status: ""               # Sanity test result
    dev_testing_status: ""          # Testing summary
    test_report_link: ""            # Test report URL

  impact_analysis:
    internal: ""                    # Internal impact
    external: ""                    # Customer impact
    security: ""                    # Security considerations

  checklist:
    api_documentation: false        # API docs updated?
    enterprise_portal: false        # Portal updated?
    bi_dashboard: false             # BI dashboard changes?
    billing_query: false            # Billing impact?
    batch_processing_engine: false  # Batch engine impact?
    live_clients_impacted: false    # Client impact?

  deployment:
    pre_requisites:
      - ""                          # Pre-deployment steps
    rollback_method:
      - ""                          # Rollback steps
    post_deployment_testing:
      - ""                          # Post-deploy validation
    monitoring_details: ""          # Monitoring approach

  communication:
    internal_stakeholders:
      - ""                          # Internal notifications
    external_stakeholders:
      - ""                          # Client notifications
    notification_required: false    # Notification needed?


```