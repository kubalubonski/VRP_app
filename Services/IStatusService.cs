namespace OptymalizacjaTras.Services
{
    public interface IStatusService
    {
        Task UpdateStatusAsync(string message);
        Task SetErrorAsync(string errorMessage);
        Task SetCompletedAsync(string completionMessage);
        Task<string> GetCurrentStatusAsync();
        bool IsProcessing();
        bool IsCompleted();
        bool HasError();
    }
}
