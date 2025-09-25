import asyncio
from .executor import ExecutorAgent

class OrchestratorAgent:
    async def execute_tests(self, tests: list, run_id: str, repeats: int = 2) -> list:
        executors = [ExecutorAgent("exec-1"), ExecutorAgent("exec-2")]
        all_results = []

        for i, test in enumerate(tests):
            tasks = []
            for r in range(repeats):
                ex = executors[(i + r) % len(executors)]
                tasks.append(ex.run_test(test, run_id))
            run_results = await asyncio.gather(*tasks)
            all_results.append({
                "test_id": test.get("id"),
                "test_case": test,
                "runs": run_results
            })
        return all_results
