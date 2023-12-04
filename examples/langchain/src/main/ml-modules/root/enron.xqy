xquery version "1.0-ml";

module namespace ex = "org:example";

(:
Lots of hacking in here to attempt to extract meaningful and reasonably sized
"chunks" of text from each email. 
:)
declare function ex:transform(
  $content as map:map,
  $context as map:map
) as map:map*
{
    let $doc := fn:string(map:get($content, "value"))
    let $doc := (fn:substring-before($doc, "Original Message"), $doc)[2]
    let $doc := (fn:substring-before($doc, "Request ID"), $doc)[2]
    let $doc := (fn:substring-after($doc, "Content-Type:"), $doc)[2]
    let $doc := (fn:substring-after($doc, "Subject:"), $doc)[2]
    let $doc := (fn:substring-after($doc, "X-FileName"), $doc)[2]
    let $chunks := 
        for $chunk in fn:tokenize($doc, "\n\n")
        where fn:string-length($chunk) > 500 and fn:string-length($chunk) < 2000
        return $chunk
    
    let $_ := 
        for $chunk in $chunks[2 to fn:last()]
        return xdmp:document-insert("/chunk/" || sem:uuid-string() || ".txt", 
            document{$chunk},
            (xdmp:permission("rest-reader", "read"), xdmp:permission("rest-writer", "update")),
            ("enron", "chunk")
        )
    
    let $_ := map:put($content, "value", document{$chunks[1]})
    return $content
};