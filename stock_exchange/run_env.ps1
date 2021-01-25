invoke-expression "net start mysql80"

invoke-expression "cmd /c start powershell -NoExit -Command {
    cd 'E:\!STUDIA\7 SEMESTR\Projekt Dyplomowy\stockapp\Scripts';
    .\activate;
    cd 'E:\!STUDIA\7 SEMESTR\Projekt Dyplomowy\stock_exchange';
    python .\manage.py runserver 5005;
}";

invoke-expression "cmd /c start powershell -NoExit -Command {
    cd 'E:\!STUDIA\7 SEMESTR\Projekt Dyplomowy\stockapp\Scripts';
    .\activate;
    cd 'E:\!STUDIA\7 SEMESTR\Projekt Dyplomowy\stock_exchange';
    celery -A stock_exchange worker -l info;
}";

invoke-expression "cmd /c start powershell -NoExit -Command {
    cd 'E:\!STUDIA\7 SEMESTR\Projekt Dyplomowy\stockapp\Scripts';
    .\activate;
    cd 'E:\!STUDIA\7 SEMESTR\Projekt Dyplomowy\stock_exchange';
    celery -A stock_exchange beat;
}";
exit;