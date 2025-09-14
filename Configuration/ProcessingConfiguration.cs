namespace OptymalizacjaTras.Configuration
{
    public class ProcessingConfiguration
    {
        public string PythonExecutable { get; set; } = "python";
        public PythonScriptConfiguration Scripts { get; set; } = new();
        public int ProcessTimeoutMs { get; set; } = 300000; // 5 minutes
        public int StatusCheckIntervalMs { get; set; } = 2000; // 2 seconds for JavaScript polling
    }

    public class PythonScriptConfiguration
    {
        public string GeocodeScript { get; set; } = "PythonScripts/geocode.py";
        public string RouteTimesScript { get; set; } = "PythonScripts/route_times.py";
        public string ScenariosScript { get; set; } = "PythonScripts/czasy_przejazdu_perturb.py";
    }
}
