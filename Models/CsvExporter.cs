namespace OptymalizacjaTras.Models;

public class CsvExporter
{
    public static void ExportDaneWejsciowe(DaneWejsciowe dane, string filePath)
    {
        using var sw = new System.IO.StreamWriter(filePath, false, System.Text.Encoding.UTF8);
        // Nagłówki
        sw.WriteLine("Typ,Ulica,Numer,Miasto,KodPocztowy,OknoCzasoweOd,OknoCzasoweDo");
        // Magazyn
        sw.WriteLine($"Magazyn,{dane.UlicaMagazynu},{dane.NumerMagazynu},{dane.MiastoMagazynu},{dane.KodPocztowyMagazynu},,");
        // Punkty dostaw
        foreach (var p in dane.PunktyDostaw)
        {
            sw.WriteLine($"PunktDostawy,{p.Ulica},{p.Numer},{p.Miasto},{p.KodPocztowy},{p.OknoCzasoweOd},{p.OknoCzasoweDo}");
        }
    }
}
