using OptymalizacjaTras.Models;

namespace OptymalizacjaTras.Services
{
    public interface IProcessingService
    {
        Task<bool> ExecuteWorkflowAsync(DaneWejsciowe dane);
        Task<bool> ExecuteGeocodingAsync();
        Task<bool> ExecuteRoutingAsync();
        Task<bool> ExecuteScenariosAsync();
    }
}
