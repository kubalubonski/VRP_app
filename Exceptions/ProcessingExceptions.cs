using System.Collections.Generic;

namespace OptymalizacjaTras.Exceptions
{
    public class ProcessingException : Exception
    {
        public string OperationName { get; }
        public int? ExitCode { get; protected set; }

        public ProcessingException(string operationName, string message) 
            : base(message)
        {
            OperationName = operationName;
        }

        public ProcessingException(string operationName, string message, Exception innerException) 
            : base(message, innerException)
        {
            OperationName = operationName;
        }

        public ProcessingException(string operationName, int exitCode, string message) 
            : base(message)
        {
            OperationName = operationName;
            ExitCode = exitCode;
        }
    }

    public class ApiLimitExceededException : ProcessingException
    {
        public ApiLimitExceededException(string operationName) 
            : base(operationName, $"{operationName}: Przekroczono limit API - spróbuj za kilka minut")
        {
            ExitCode = 2;
        }
    }

    public class ValidationException : Exception
    {
        public List<string> ValidationErrors { get; }

        public ValidationException(List<string> errors) 
            : base($"Błędy walidacji: {string.Join(", ", errors)}")
        {
            ValidationErrors = errors;
        }

        public ValidationException(string error) 
            : base($"Błąd walidacji: {error}")
        {
            ValidationErrors = new List<string> { error };
        }
    }

    public class FileProcessingException : Exception
    {
        public string FilePath { get; }

        public FileProcessingException(string filePath, string message) 
            : base(message)
        {
            FilePath = filePath;
        }

        public FileProcessingException(string filePath, string message, Exception innerException) 
            : base(message, innerException)
        {
            FilePath = filePath;
        }
    }
}
