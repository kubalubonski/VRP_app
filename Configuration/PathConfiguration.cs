namespace OptymalizacjaTras.Configuration
{
    public class PathConfiguration
    {
        public string DataFilePath { get; set; } = "wwwroot/dane_wejsciowe.csv";
        public string ConfigFilePath { get; set; } = "wwwroot/config.csv";
        public string StatusFilePath { get; set; } = "wwwroot/processing_status.txt";
        public string LogDirectory { get; set; } = "Logs";
        public string ApplicationLogFile { get; set; } = "log_aplikacja.txt";
        public string PythonLogFile { get; set; } = "log_python.txt";
        public string SampleDataPath { get; set; } = "PlanyInstrukcje/trasy_przykladowe.csv";
        public string RoutesDirectory { get; set; } = "wwwroot/trasy";
        
        public string GetFullLogPath(string logFile)
        {
            return Path.Combine(Directory.GetCurrentDirectory(), LogDirectory, logFile);
        }
        
        public string GetFullPath(string relativePath)
        {
            return Path.Combine(Directory.GetCurrentDirectory(), relativePath);
        }
    }
}
