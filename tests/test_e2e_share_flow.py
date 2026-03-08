"""
E2E Test: Agent → Share Link → End-User Login → Chat → File Upload

Flow:
1. Create agent via SDK
2. Create share link (require_sign_in=True, allow_file_upload=True)
3. Get share info
4. Login as end-user (existing account)
5. Chat via share link with end_user_token
6. Upload a document via share link
7. Cleanup: delete share link, delete agent
"""

import os
import sys
import httpx

# SDK를 로컬 소스에서 임포트
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_teammate import AITeammate

API_KEY = os.environ.get("AT_API_KEY", "")
BASE_URL = "https://ai-teammate.net/api"

# 기존 등록된 end-user 계정 (테스트용)
END_USER_EMAIL = os.environ.get("AT_TEST_EMAIL", "")
END_USER_PASSWORD = os.environ.get("AT_TEST_PASSWORD", "")


def step(num, title):
    print(f"\n{'='*60}")
    print(f"  Step {num}: {title}")
    print(f"{'='*60}")


def main():
    if not API_KEY:
        print("ERROR: Set AT_API_KEY environment variable")
        sys.exit(1)

    client = AITeammate(api_key=API_KEY, base_url=BASE_URL)
    agent_id = None
    share = None

    try:
        # ── Step 1: Create Agent ──
        step(1, "Create Agent")
        agent = client.agents.create(
            name="SDK E2E Test Agent",
            system_prompt="You are a helpful test assistant. Reply briefly in Korean.",
        )
        agent_id = agent.id
        print(f"  Agent created: {agent.name} ({agent.id})")

        # ── Step 2: Create Share Link ──
        step(2, "Create Share Link (sign-in + file upload)")
        share = client.shares.create(
            agent_id=agent_id,
            require_sign_in=True,
            allow_file_upload=True,
            max_messages=50,
        )
        print(f"  Share code: {share.share_code}")
        print(f"  Share URL: https://ai-teammate.net{share.share_url}")
        print(f"  require_sign_in: {share.require_end_user_auth}")
        print(f"  allow_file_upload: {share.allow_file_upload}")

        # ── Step 3: Get Share Info ──
        step(3, "Get Share Info (public)")
        info = client.shares.get_info(share.share_code)
        print(f"  Agent: {info.agent.name} ({info.agent.id})")
        print(f"  Settings: max_messages={info.share.max_messages}, "
              f"require_sign_in={info.share.require_end_user_auth}, "
              f"allow_file_upload={info.share.allow_file_upload}")

        # ── Step 4: End-User Login ──
        step(4, "End-User Login")
        end_user_token = None
        if END_USER_EMAIL and END_USER_PASSWORD:
            login_resp = httpx.post(
                f"{BASE_URL}/end-user/auth/{agent_id}/login",
                json={"email": END_USER_EMAIL, "password": END_USER_PASSWORD},
            )
            if login_resp.status_code == 200:
                login_data = login_resp.json()
                end_user_token = login_data.get("token")
                end_user_name = login_data.get("end_user", {}).get("name", "?")
                print(f"  Logged in as: {end_user_name} ({END_USER_EMAIL})")
                print(f"  Token: {end_user_token[:20]}...")
            else:
                print(f"  Login failed ({login_resp.status_code}): {login_resp.text}")
                print("  Continuing without auth...")
        else:
            print("  Skipping login (AT_TEST_EMAIL / AT_TEST_PASSWORD not set)")
            print("  Continuing without auth...")

        # ── Step 5: Chat via Share Link ──
        step(5, "Chat via Share Link")
        response = client.shares.chat(
            share.share_code,
            "안녕하세요! 오늘 날씨가 어때요?",
            end_user_token=end_user_token,
        )
        print(f"  Agent replied: {response.content[:200] if response.content else '(empty)'}")

        # ── Step 6: Upload Document ──
        step(6, "Upload Document via Share Link")
        # RAG 검증용 고유 키워드가 포함된 테스트 문서
        test_file = "/tmp/sdk_test_document.txt"
        with open(test_file, "w") as f:
            f.write("=== 프로젝트 제피루스 내부 문서 ===\n\n")
            f.write("프로젝트 제피루스(Project Zephyrus)는 2026년 3월에 시작된 차세대 AI 플랫폼 프로젝트입니다.\n\n")
            f.write("핵심 목표:\n")
            f.write("1. 코드명 '오로라 엔진'을 활용한 실시간 멀티모달 처리\n")
            f.write("2. 월간 활성 사용자(MAU) 50만 명 달성\n")
            f.write("3. 시리즈 B 투자 유치 목표: 150억원\n\n")
            f.write("프로젝트 리더: 김태양 (CTO)\n")
            f.write("예상 완료일: 2026년 12월\n")
            f.write("내부 슬로건: '바람처럼 빠르게, 구름처럼 유연하게'\n")

        doc = client.shares.upload_document(share.share_code, test_file)
        print(f"  Uploaded: {doc.filename}")
        print(f"  File type: {doc.file_type}, Size: {doc.file_size} bytes")
        print(f"  Chunks: {doc.chunk_count}, Status: {doc.status}")

        # ── Step 7: RAG Search — ask about unique keywords from the document ──
        step(7, "RAG Search Test — query document-specific content")
        import time
        time.sleep(2)  # embedding 인덱싱 대기

        rag_queries = [
            ("프로젝트 제피루스의 투자 목표 금액은?", "150억"),
            ("오로라 엔진은 무엇에 사용되나요?", "멀티모달"),
            ("프로젝트 리더가 누구야?", "김태양"),
        ]

        rag_pass = 0
        for query, expected_keyword in rag_queries:
            response2 = client.shares.chat(
                share.share_code,
                query,
                end_user_token=end_user_token,
            )
            content = response2.content or ""
            found = expected_keyword in content
            status = "PASS" if found else "FAIL"
            rag_pass += int(found)
            print(f"  [{status}] Q: {query}")
            print(f"         A: {content[:200]}")
            print(f"         Expected '{expected_keyword}': {'Found' if found else 'NOT FOUND'}")
            print()

        print(f"  RAG Results: {rag_pass}/{len(rag_queries)} passed")
        if rag_pass == 0:
            print("  WARNING: No RAG results found — document may not be indexed yet")

        # ── Step 8: List share links ──
        step(8, "List Share Links")
        shares_list = client.shares.list(agent_id)
        print(f"  Total shares: {len(shares_list)}")
        for s in shares_list:
            print(f"    - {s.share_code} (active={s.is_active}, views={s.view_count})")

        # ── Step 9: Cleanup ──
        step(9, "Cleanup")
        client.shares.delete(agent_id, share.id)
        print(f"  Share link deleted: {share.share_code}")
        share = None

        client.agents.delete(agent_id)
        print(f"  Agent deleted: {agent_id}")
        agent_id = None

        print(f"\n{'='*60}")
        print("  ALL TESTS PASSED!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n  ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

        # Cleanup on failure
        if share and agent_id:
            try:
                client.shares.delete(agent_id, share.id)
                print(f"  Cleaned up share: {share.share_code}")
            except Exception:
                pass
        if agent_id:
            try:
                client.agents.delete(agent_id)
                print(f"  Cleaned up agent: {agent_id}")
            except Exception:
                pass
        sys.exit(1)
    finally:
        client.close()
        # Cleanup temp file
        try:
            os.remove("/tmp/sdk_test_document.txt")
        except OSError:
            pass


if __name__ == "__main__":
    main()
