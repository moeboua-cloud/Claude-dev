# Demo Scenarios

The mock data includes 10 pre-configured scenarios that demonstrate the platform's capabilities.

## Scenario 1: New Hire Missing Baseline Access

**User**: Priya Patel (EMP007) - Registered Nurse, new hire
**Issue**: Missing `GRP-Clinical-Users` and `APP-Epic-ClinicalUser`
**Expected**: Clinical Staff persona baseline includes Epic access

**Try**: `"Why does Priya Patel not have Epic access?"`

## Scenario 2: Mover Retaining Old Department Access

**User**: David Kim (EMP004) - Moved from Finance to IT (Software Engineering)
**Issue**: Still has `GRP-Finance-Users`, `DL-Finance-Team`, `APP-SAP-Users` from old role
**Expected**: Should only have Software Engineer persona baseline

**Try**: `"What changed after David Kim moved from Finance to IT?"`

## Scenario 3: Excess Privileged Group Membership

**User**: John Smith (EMP002) - IT Systems Administrator
**Issue**: Has `GRP-DomainAdmins` which is not in his persona baseline
**Risk**: Critical - Domain Admin is a highest-privilege group

**Try**: `"Which entitlements look excessive for John Smith?"`

## Scenario 4: Missing Required Baseline Group

**User**: James Wilson (EMP006) - Security Operations Analyst
**Issue**: Missing `APP-Jira-Users` from his SecOps baseline
**Expected**: SecOps persona includes Jira access

**Try**: `"Compare James Wilson's access to his expected baseline"`

## Scenario 5: Exception Entitlement Needing Review

**User**: Lisa Johnson (EMP005) - HR Business Partner
**Issue**: Has `APP-Workday-HRAdmin` as an approved exception
**Expected**: Periodic review of exception entitlements

**Try**: `"Show me Lisa Johnson's access details"`

## Scenario 6: Contractor with Privileged Access

**User**: Bob External (EMP008) - Contract Developer
**Issue**: Has `PAM-ServerAdmins` which violates contractor policy
**Policy**: Contractors cannot hold privileged group memberships

**Try**: `"Recommend cleanup for Bob External"`

## Scenario 7: Analyst Asks Why Access Is Missing

**Try**: `"Why does Sarah not have Epic access?"`
Sarah Chen (Finance) is not in the Clinical persona, so Epic is not in her baseline.

## Scenario 8: Analyst Asks Why Excess Access Exists

**Try**: `"Why does John Smith have Domain Admin access?"`
Domain Admin is not part of the IT SysAdmin persona baseline.

## Scenario 9: Manager Approval for Recommended Removal

1. Generate recommendations for John Smith (EMP002)
2. The Domain Admin excess will appear as a critical recommendation
3. Submit for approval via the Recommendations page
4. Approve or reject via the Approvals page

## Scenario 10: Approved Action Executed in Simulation Mode

1. Approve a low-risk recommendation
2. Execute the action
3. The system runs in simulation mode and logs what would happen
4. Check the Audit Log for the full decision trail
