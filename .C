



if ((bufptr[DF_Command-1] & 0xc0) ==0x00)
{
    Dpressure    = ((unsigned int) (bufptr[DF_Command-1] & 0x3f) << 8) + (bufptr[DF_Command-2]);
    Dtemperature = (((unsigned int) bufptr[DF_Command-3]) << 3) + bufptr[DF_Command-4];
    Pressure     = (((float) Dpressure) - P1) * (Pmax - Pmin) / P2 + Pmin;
    Temperatur   = ((float) Dtemperature) * 200 / 2047 - 50;
}


if ((bufptr[DF_Command-1] & 0xc0) ==0x00)
{
    Dpressure    = ((unsigned int) (bufptr[DF_Command-1] & 0x3f) << 8) + (bufptr[DF_Command-2]);
    Dtemperature = (((unsigned int) bufptr[DF_Command-3]) << 3) + (bufptr[DF_Command-4] >> 5);
    Pressure     = (((float) Dpressure) - P1) * (Pmax - Pmin) / P2 + Pmin;
    Temperatur   = ((float) Dtemperature) * 200 / 2047 - 50;
}