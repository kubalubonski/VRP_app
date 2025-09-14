using System.Diagnostics;
using Microsoft.Extensions.Options;
using OptymalizacjaTras.Models;
using OptymalizacjaTras.Configuration;
using OptymalizacjaTras.Exceptions;

namespace OptymalizacjaTras.Services
{
    public class ProcessingService : IProcessingService
    {
        private readonly IStatusService _statusService;
        private readonly ILogger<ProcessingService> _logger;
        private readonly PathConfiguration _pathConfig;
        private readonly ProcessingConfiguration _processingConfig;

        public ProcessingService(IStatusService statusService, ILogger<ProcessingService> logger, 
            IOptions<PathConfiguration> pathConfig, IOptions<ProcessingConfiguration> processingConfig)
        {
            _statusService = statusService;
            _logger = logger;
            _pathConfig = pathConfig.Value;
            _processingConfig = processingConfig.Value;
        }

        public async Task<bool> ExecuteWorkflowAsync(DaneWejsciowe dane)
        {
            try
            {
                _logger.LogInformation("[START] Workflow rozpoczęty");
                
                // Eksport danych do CSV
                string filePath = _pathConfig.GetFullPath(_pathConfig.DataFilePath);
                CsvExporter.ExportDaneWejsciowe(dane, filePath);
                _logger.LogInformation("Eksport danych do CSV: OK");

                // Zapisz konfigurację
                string configPath = _pathConfig.GetFullPath(_pathConfig.ConfigFilePath);
                File.WriteAllText(configPath, $"LiczbaPojazdow,{dane.LiczbaPojazdow}\n");

                await _statusService.UpdateStatusAsync("🚀 Rozpoczynanie przetwarzania - przygotowywanie danych...");

                // ETAP 1: GEOKODOWANIE
                await _statusService.UpdateStatusAsync("🌍 Geokodowanie adresów - konwersja na współrzędne GPS...");
                var success1 = await ExecuteGeocodingAsync();
                if (!success1) return false;

                // ETAP 2: POBIERANIE CZASÓW
                await _statusService.UpdateStatusAsync("✅ Geokodowanie ukończone! 🚗 Pobieranie czasów przejazdu z API...");
                var success2 = await ExecuteRoutingAsync();
                if (!success2) return false;

                // ETAP 3: SCENARIUSZE
                await _statusService.UpdateStatusAsync("✅ Pobieranie czasów ukończone! ⚡ Generowanie scenariuszy czasowych...");
                var success3 = await ExecuteScenariosAsync();
                if (!success3) return false;

                // KONIEC
                await _statusService.SetCompletedAsync("🎉 Wszystkie etapy zakończone pomyślnie! Dane gotowe do pobrania.");
                _logger.LogInformation("[END] Workflow zakończony pomyślnie");
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "[ERROR] Błąd podczas wykonywania workflow");
                await _statusService.SetErrorAsync($"Błąd podczas przetwarzania: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> ExecuteGeocodingAsync()
        {
            try
            {
                return await ExecutePythonScriptAsync(_processingConfig.Scripts.GeocodeScript, "Geokodowanie");
            }
            catch (ProcessingException ex)
            {
                _logger.LogError(ex, "Błąd podczas geokodowania");
                await _statusService.SetErrorAsync(ex.Message);
                return false;
            }
        }

        public async Task<bool> ExecuteRoutingAsync()
        {
            try
            {
                return await ExecutePythonScriptAsync(_processingConfig.Scripts.RouteTimesScript, "Pobieranie czasów");
            }
            catch (ProcessingException ex)
            {
                _logger.LogError(ex, "Błąd podczas pobierania czasów");
                await _statusService.SetErrorAsync(ex.Message);
                return false;
            }
        }

        public async Task<bool> ExecuteScenariosAsync()
        {
            try
            {
                return await ExecutePythonScriptAsync(_processingConfig.Scripts.ScenariosScript, "Scenariusze czasowe");
            }
            catch (ProcessingException ex)
            {
                _logger.LogError(ex, "Błąd podczas generowania scenariuszy");
                await _statusService.SetErrorAsync(ex.Message);
                return false;
            }
        }

        private async Task<bool> ExecutePythonScriptAsync(string scriptPath, string operationName)
        {
            var processInfo = new ProcessStartInfo
            {
                FileName = _processingConfig.PythonExecutable,
                Arguments = scriptPath,
                WorkingDirectory = Directory.GetCurrentDirectory(),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            try
            {
                using var process = Process.Start(processInfo);
                if (process == null)
                {
                    throw new ProcessingException(operationName, "Nie udało się uruchomić procesu Python");
                }

                await process.WaitForExitAsync();
                
                switch (process.ExitCode)
                {
                    case 0:
                        _logger.LogInformation($"{operationName}: OK");
                        return true;
                    case 2:
                        throw new ApiLimitExceededException(operationName);
                    default:
                        throw new ProcessingException(operationName, process.ExitCode, 
                            $"{operationName}: Wystąpił błąd (kod: {process.ExitCode})");
                }
            }
            catch (ProcessingException)
            {
                throw; // Re-throw processing exceptions
            }
            catch (Exception ex)
            {
                throw new ProcessingException(operationName, $"BŁĄD uruchamiania skryptu: {ex.Message}", ex);
            }
        }
    }
}
