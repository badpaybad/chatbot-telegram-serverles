import asyncio
import sys
import os
import json
from unittest.mock import MagicMock, AsyncMock, patch

# Add the project root to sys.path
sys.path.append(os.getcwd())

import skills.jira.tool_call_jira as tool_call_jira

async def test_jira_assignee_logic():
    print("--- Starting Jira Assignee Logic Test (Robust) ---")
    
    # Mock data
    issue_data = {
        "should_create": True,
        "summary": "Test Task",
        "description": "Test Description",
        "issuetype": "Task",
        "duedate": "2026-03-05",
        "assignee": "dunp"
    }
    
    # Mock httpx.AsyncClient context manager
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__ = AsyncMock()
        mock_instance.post = AsyncMock()
        
        # Scenario 1: Success with all fields
        print("\nScenario 1: Success with all fields")
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 201
        mock_resp1.json.return_value = {"key": "PROJ-123"}
        mock_instance.post.return_value = mock_resp1
        
        result = await tool_call_jira.create_jira_issue(issue_data)
        print(f"Result 1: {result}")
        assert "PROJ-123" in result
        
        # Verify payload
        args, kwargs = mock_instance.post.call_args
        payload = kwargs["json"]
        print(f"Payload 1: {json.dumps(payload, indent=2)}")
        assert payload["fields"]["assignee"] == {"name": "dunp"}
        assert payload["fields"]["duedate"] == "2026-03-05"
        
        # Scenario 2: Failure with assignee, success on retry
        print("\nScenario 2: Failure with assignee, success on retry")
        mock_instance.post.reset_mock()
        mock_resp_fail_assignee = MagicMock()
        mock_resp_fail_assignee.status_code = 400
        mock_resp_fail_assignee.text = "Field 'assignee' is not allowed"
        
        mock_resp_success_2 = MagicMock()
        mock_resp_success_2.status_code = 201
        mock_resp_success_2.json.return_value = {"key": "PROJ-124"}
        
        mock_instance.post.side_effect = [mock_resp_fail_assignee, mock_resp_success_2]
        
        result = await tool_call_jira.create_jira_issue(issue_data)
        print(f"Result 2: {result}")
        assert "PROJ-124" in result
        assert mock_instance.post.call_count == 2
        
        # Verify second payload does not have assignee
        args, kwargs = mock_instance.post.call_args
        payload = kwargs["json"]
        print(f"Payload 2 (Retry): {json.dumps(payload, indent=2)}")
        assert "assignee" not in payload["fields"]
        assert "duedate" in payload["fields"]

        # Scenario 3: Failure with both, success on retry
        print("\nScenario 3: Failure with both, success on retry")
        mock_instance.post.reset_mock()
        mock_instance.post.side_effect = None
        
        mock_resp_fail_both = MagicMock()
        mock_resp_fail_both.status_code = 400
        mock_resp_fail_both.text = "Fields 'assignee' and 'duedate' are not allowed"
        
        mock_resp_success_3 = MagicMock()
        mock_resp_success_3.status_code = 201
        mock_resp_success_3.json.return_value = {"key": "PROJ-125"}
        
        mock_instance.post.side_effect = [mock_resp_fail_both, mock_resp_success_3]
        
        result = await tool_call_jira.create_jira_issue(issue_data)
        print(f"Result 3: {result}")
        assert "PROJ-125" in result
        assert mock_instance.post.call_count == 2
        
        # Verify second payload does not have assignee nor duedate
        args, kwargs = mock_instance.post.call_args
        payload = kwargs["json"]
        print(f"Payload 3 (Retry): {json.dumps(payload, indent=2)}")
        assert "assignee" not in payload["fields"]
        assert "duedate" not in payload["fields"]

    print("\n--- Jira Assignee Logic Test (Robust) Passed ---")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "config_dunp":
        print("Usage: python test/test_jira_assignee.py config_dunp")
        sys.exit(1)
        
    asyncio.run(test_jira_assignee_logic())
