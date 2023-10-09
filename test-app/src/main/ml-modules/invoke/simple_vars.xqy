xquery version "1.0-ml";

declare variable $word1 as xs:string external;
declare variable $word2 as xs:string external;

($word1, $word2, fn:concat($word1, " ", $word2))