# Huffman-archiver

## Запуск программы
- Отобразить возможные параметры работы программы

    ```python3 main.py --help```

    
- Сжать файл

    ```python3 main.py --compress path```

- Разархивировать файл

    ```python3 main.py --decompress path ```
- Ключ ```--verbose``` к выводу добавится отладочная информация.

    Крайне не рекомендуется запускать с ```-v``` на больших файлах.
    Если всё-таки надо, то 
    
    ```python3 main.py -c path -v > output.txt```

## Алгорим cжатия:
    
Cчитываем бинарно файл, далее считаем частоты байт, создаём словар ***{байт: частота}***, строим дерево Хаффмана по частотам. Обходя итоговое дерево строятся новые коды для исходных байтов ***{старый_байт: новый_код}***.

Преобразовываем входной файл по новым кодам: просто проходимся по байтам и мапим по дикту ***{старый_байт: новый_код}***.

Нужно сохранить в файл итоговый таблицу трансляции кодов, для обратного разархивирования.

Формат выходного файла:

```[cl_1][c_1][b_1]...[cl_n][c_n][b_n]000000000[tl][type][encoded_file][zeros][cnt_zeros]```

где:
- **cl_i** -- (9 бит) размер в битах **c_i**
- **c_i** -- (cl_i бит) код хаффмана для байта **b_i**
- **b_i** -- (8 бит) символ исходного файла для **c_i**
- **000000000** -- (9 бит) 9 нулей для обозначения конца таблицы хаффмана
- **tl** -- (8 бит) размер в байтах **type**
- **type** -- (tl байт) исходное раширение файла
- **encoded_file** -- двоичный код файла в коде хаффмана
- **zeros** -- нули для выравнивания до байта
- **cnt_zeros** -- (8 бит) размер в битах **zeros**

## Сравнение архиваторов

|Название файла|Размер файла|RAR|ZIP|ZMH|TAR|
|-|-:|-:|-:|-:|-:|
|test_mycode.py|7884 Byte|1946 Byte|2065 Byte|4707 Byte|121815040 Byte|
|test_image.png|4192182 Byte|4048423 Byte|4076443 Byte|4120624 Byte|243630080 Byte|
|test_song.mp3|7381266 Byte|6706980 Byte|6730100 Byte|7096876 Byte|487260160 Byte|
|test_empty.txt|0 Byte|73 Byte|208 Byte|7 Byte|974520320 Byte|
|test_big_file.txt|10406880 Byte|8249 Byte|81967 Byte|5938724 Byte|1949040640 Byte|
|test_big_same.txt|18295200 Byte|45147 Byte|85349 Byte|3415118 Byte|3898081280 Byte|
|test_one_char.txt|9 Byte|85 Byte|217 Byte|10 Byte|7796172800 Byte|

Из полученых результатов можно сделать следующие ввыводы:
- Изображения уже хорошо сжаты, почти бессмысленно сжимать их архиваторами
- При сжатии больших файлов видно, что zmh отлично справляется с задачей, но до RAR и ZIP ему ещё далеко
- Чобы добиться лучших результатов сжатия zmh можно при кодировании детектировать повторяющиеся последовательности символы, а не отдельные символы, тогда сжатие будет более сильным в хороших случаях, но это уже совсем другая история)
- **Временная оценка**
    - Трудно оценить какая разница во времени сжатия и разжатия различными архиваторами, эмперически было выявлено:
        - сжатие zmh по скорости не уступает сжатию zip
        - разархивирование zmh занимает больше времени, чем zip 
            - на больших файлах, разница чувствутся: некоторые файлы zip за 3 секунды разархивирует, а zmh за 20 секунд
