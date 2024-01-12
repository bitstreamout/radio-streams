# Radio Streams

This is a fork of the project of **Sven Festersen**:

> A small server to proxy audio (radio station) streams. I had to write this
> because my DLNA-enabled AV receiver does not support radio streams without
> file extension...

Now I had a similar problem with my older **Marantz M-CR610** and the Canadian
Internet radio station **JB-Radio**[^1]. First of all the **M-CR610** can play
flac audio format but not via Internet Radio Option. Beside this the flac is embedded in
an ogg transport stream.  Nevertheless there are also mp3 and aac streams available.
The only problem was that the **M-CR610** always disconnect from the resulting
http connection [https://maggie.torontocast.com:8076/aac](https://maggie.torontocast.com:8076/aac).
I identified two problems, first of all there *is* no file extension and second
the metadata delivered in the http get request shows `Content-Type: audio/aacp`.

With a view changes of the proxy code and overwriting the http header handling
of the python tornado library (do not change icy- and ice- lowercase tags) and
change the mime code from `audio/aacp` to `audio/aac` the **M-CR610** can now
play the `aac` stream of **JB-Radio**.  Together with `ThHanika/YCast` (https://github.com/ThHanika/YCast)
which provides a replacement of the `vTuner` only Internet Radio Option of the **M-CR610**.

I now use both the **YCast** self hosted vTuner internet radio service and this **radio streams**
proxy as container on my local **NAS**.

## References
[^1]: [https://jb-radio.net/](https://jb-radio.net/)

## Usage
Create a JSON file (e.g. `streams.json`) in the following format:

```
{
  "station1": [ "http://url/for/station1", "mp3"],
  "station2": [ "http://url/for/station2", "aac"]
}
```

Start the server:

```
stream-proxy --port 8080 --address=localhost streams.json
```

The streams will then be available at "http://localhost:8080/radio/station1.mp3"
and "http://localhost:8080/radio/station2.aac".

