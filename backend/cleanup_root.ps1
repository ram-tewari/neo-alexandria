# Cleanup Backend Root Directory
# This script removes temporary files, test scripts, and consolidates documentation

Write-Host "🧹 Cleaning up backend root directory..." -ForegroundColor Cyan
Write-Host ""

$filesToDelete = @(
    # Test output files
    "auth_test_output.txt",
    "benchmark_output.txt",
    "chunking_pipeline_output.txt",
    "full_test_output.txt",
    "performance_results.txt",
    "resource_test_output.txt",
    "stability_test_output.txt",
    "test_output.txt",
    "test_results.txt",
    "test_token.txt",
    "server_pid.txt",
    
    # JSON output files
    "performance_ragas_results_20260113_113650.json",
    "performance_ragas_results_20260113_140728.json",
    "performance_ragas_results_20260113_140752.json",
    "performance_ragas_results_20260113_154236.json",
    "test_results_detailed_20260113_113336.json",
    "test_results_detailed_20260113_133331.json",
    "rollback_log.json",
    
    # Redundant deployment docs (consolidated into docs/guides/deployment.md)
    "DEPLOY_NOW.md",
    "DEPLOY_TO_RENDER.md",
    "DEPLOYMENT_CHECKLIST.md",
    "DEPLOYMENT_NEXT_STEPS.md",
    "DEPLOYMENT_PUSHED.md",
    "DEPLOYMENT_ROADMAP.md",
    "DEPLOYMENT_STATUS.md",
    "START_DEPLOYMENT.md",
    "RENDER_DEPLOYMENT_CHECKLIST.md",
    "PHASE19_DEPLOYMENT_README.md",
    "PHASE19_DEPLOYMENT_SUMMARY.md",
    "PHASE19_STAGING_DEPLOYMENT_PLAN.md",
    
    # Redundant test/status docs (consolidated into docs/guides/testing-history.md)
    "CHUNKING_FINAL_REPORT.md",
    "CHUNKING_STATUS.md",
    "CHUNKING_VERIFICATION.md",
    "COMPREHENSIVE_TEST_REPORT.md",
    "CRITICAL_FIXES_APPLIED.md",
    "ENDPOINT_TEST_RESULTS.md",
    "FINAL_STATUS.md",
    "P0_COMPLETION_SUMMARY.md",
    "P0_FIXES_VERIFIED.md",
    "PHASE19_INTEGRATION_TESTS_COMPLETE.md",
    "PHASE19_INTEGRATION_TESTS_STATUS.md",
    "PHASE19_INTEGRATION_TESTS_SUMMARY.md",
    "PHASE19_PERFORMANCE_TESTING_SUMMARY.md",
    "PHASE19_WSL_TEST_RESULTS.md",
    "PHASE19_GRAPH_SERVICE_VERIFICATION.md",
    "TEST_RESULTS_SUMMARY.md",
    "WORK_COMPLETED_SUMMARY.md",
    "PRODUCTION_READINESS_ASSESSMENT.md",
    
    # One-off test scripts (moved to tests/ or archived)
    "test_all_endpoints.py",
    "test_api_create.py",
    "test_benchmark.py",
    "test_check_routes.py",
    "test_chunk_details.py",
    "test_chunking_e2e_simple.py",
    "test_chunking_e2e.py",
    "test_chunking_final_verification.py",
    "test_chunking_final.py",
    "test_chunking_fix.py",
    "test_chunking_simple.py",
    "test_chunking_speed.py",
    "test_chunking_verification.py",
    "test_chunking_wait_ingestion.py",
    "test_chunking_works.py",
    "test_comprehensive_endpoints.py",
    "test_db_connection.py",
    "test_detailed_modules.py",
    "test_direct_ingestion.py",
    "test_direct_insert.py",
    "test_discover_endpoints.py",
    "test_e2e_graph_generation.py",
    "test_embedding_fix.py",
    "test_endpoints_simple.py",
    "test_event_emission.py",
    "test_fixes_no_server.py",
    "test_frontend_resource.py",
    "test_ingestion_debug.py",
    "test_live_chunking_fix.py",
    "test_live_endpoints.py",
    "test_live_fixes.py",
    "test_neural_graph_standalone.py",
    "test_neural_simple.py",
    "test_performance_and_ragas.py",
    "test_postman_chunking.py",
    "test_quick_endpoints.py",
    "test_rag_quality.py",
    "test_resource_chunking.py",
    "test_resource_creation.py",
    "test_resource_endpoint.py",
    "test_server_stability.py",
    "test_simple_chunk_check.py",
    "test_stability_simple.py",
    
    # One-off utility scripts
    "add_curation_columns.py",
    "add_sample_resources.py",
    "check_chunks.py",
    "check_database.py",
    "check_db_schema.py",
    "check_live_chunks.py",
    "check_progress.py",
    "create_test_user.py",
    "debug_chunking.py",
    "fast_chunk_existing.py",
    "fix_embedding_column.py",
    "generate_test_token.py",
    "reingest_all_resources.py",
    "verify_fixes.py",
    "verify_staging_setup.py",
    
    # Redundant deployment scripts (keep only check_deployment_status.ps1)
    "test_deployment.ps1",
    "test_render_deployment.ps1",
    "monitor_deployment.ps1",
    "run_endpoint_tests.bat"
)

$deletedCount = 0
$skippedCount = 0

foreach ($file in $filesToDelete) {
    $fullPath = Join-Path $PSScriptRoot $file
    if (Test-Path $fullPath) {
        try {
            Remove-Item $fullPath -Force
            Write-Host "  Deleted: $file" -ForegroundColor Green
            $deletedCount++
        } catch {
            Write-Host "  Failed to delete: $file" -ForegroundColor Red
            $skippedCount++
        }
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Gray
        $skippedCount++
    }
}

Write-Host ""
Write-Host "Cleanup Summary:" -ForegroundColor Cyan
Write-Host "  Deleted: $deletedCount files" -ForegroundColor Green
Write-Host "  Skipped: $skippedCount files" -ForegroundColor Yellow
Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Documentation consolidated into:" -ForegroundColor Cyan
Write-Host "  - docs/guides/deployment.md (all deployment docs)" -ForegroundColor Gray
Write-Host "  - docs/guides/testing-history.md (all test results)" -ForegroundColor Gray
Write-Host ""
Write-Host "Kept essential files:" -ForegroundColor Cyan
Write-Host "  - worker.py (edge worker)" -ForegroundColor Gray
Write-Host "  - setup_edge.* (edge setup scripts)" -ForegroundColor Gray
Write-Host "  - build-and-test-edge.* (edge build scripts)" -ForegroundColor Gray
Write-Host "  - check_deployment_status.ps1 (deployment monitoring)" -ForegroundColor Gray
Write-Host "  - DEPLOYMENT_FIXES_APPLIED.md (recent fixes)" -ForegroundColor Gray
Write-Host "  - REQUIREMENTS_STRATEGY.md (dependency strategy)" -ForegroundColor Gray
Write-Host "  - NSSM_SERVICE_CONFIG.md (Windows service config)" -ForegroundColor Gray
Write-Host "  - PHASE19_*.md (Phase 19 specific docs)" -ForegroundColor Gray
