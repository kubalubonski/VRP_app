using Microsoft.Extensions.Options;
using OptymalizacjaTras.Configuration;

namespace OptymalizacjaTras.Services
{
    public class StatusService : IStatusService
    {
        private readonly string _statusFilePath;
        private readonly ILogger<StatusService> _logger;
        private readonly PathConfiguration _pathConfig;

        public StatusService(ILogger<StatusService> logger, IOptions<PathConfiguration> pathConfig)
        {
            _logger = logger;
            _pathConfig = pathConfig.Value;
            _statusFilePath = _pathConfig.GetFullPath(_pathConfig.StatusFilePath);
        }

        public async Task UpdateStatusAsync(string message)
        {
            try
            {
                await File.WriteAllTextAsync(_statusFilePath, message);
                _logger.LogInformation($"Status updated: {message}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Błąd podczas aktualizacji statusu: {message}");
            }
        }

        public async Task SetErrorAsync(string errorMessage)
        {
            var fullMessage = $"ERROR:{errorMessage}";
            await UpdateStatusAsync(fullMessage);
        }

        public async Task SetCompletedAsync(string completionMessage)
        {
            var fullMessage = $"COMPLETED:{completionMessage}";
            await UpdateStatusAsync(fullMessage);
        }

        public async Task<string> GetCurrentStatusAsync()
        {
            try
            {
                if (File.Exists(_statusFilePath))
                {
                    return await File.ReadAllTextAsync(_statusFilePath);
                }
                return string.Empty;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Błąd podczas odczytu statusu");
                return string.Empty;
            }
        }

        public bool IsProcessing()
        {
            try
            {
                if (!File.Exists(_statusFilePath)) return false;
                
                var status = File.ReadAllText(_statusFilePath);
                return !string.IsNullOrEmpty(status) && 
                       !status.StartsWith("ERROR:") && 
                       !status.StartsWith("COMPLETED:");
            }
            catch
            {
                return false;
            }
        }

        public bool IsCompleted()
        {
            try
            {
                if (!File.Exists(_statusFilePath)) return false;
                
                var status = File.ReadAllText(_statusFilePath);
                return status.StartsWith("COMPLETED:");
            }
            catch
            {
                return false;
            }
        }

        public bool HasError()
        {
            try
            {
                if (!File.Exists(_statusFilePath)) return false;
                
                var status = File.ReadAllText(_statusFilePath);
                return status.StartsWith("ERROR:");
            }
            catch
            {
                return false;
            }
        }
    }
}
