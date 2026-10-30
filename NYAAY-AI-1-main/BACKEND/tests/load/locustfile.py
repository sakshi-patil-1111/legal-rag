from locust import HttpUser, task, between

class NyaayAIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Setup common headers (e.g., Auth token)
        self.headers = {
            "Authorization": "Bearer test_dummy_token_123",
            "Content-Type": "application/json"
        }

    @task(3)
    def test_kanoon_query(self):
        payload = {
            "question": "What are my rights regarding property under Hindu Law?"
        }
        self.client.post("/api/kanoon/query", json=payload, headers=self.headers, name="Kanoon Query")

    @task(2)
    def test_drafting_generate(self):
        payload = {
            "draft_type": "legal_notice",
            "user_context": "Draft a legal notice for non-payment of rent of Rs 50,000 for 3 months."
        }
        self.client.post("/api/drafting/generate", json=payload, headers=self.headers, name="Drafting Generate")

    @task(2)
    def test_reasoning_analyze(self):
        payload = {
            "case_facts": "My neighbor built a wall encroaching 2 feet into my land.",
            "legal_question": "What is the remedy available under civil law?"
        }
        self.client.post("/api/reasoning/analyze", json=payload, headers=self.headers, name="Reasoning Analyze")

    @task(1)
    def test_upload_chat_query(self):
        payload = {
            "question": "Summarize the uploaded document.",
            "document_id": "test_doc_123"
        }
        self.client.post("/api/upload-chat/query", json=payload, headers=self.headers, name="Upload Chat Query")

    @task(1)
    def test_health_check(self):
        self.client.get("/api/health", name="Health Check")
