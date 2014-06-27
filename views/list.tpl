<html>
<head>
  <meta http-equiv="refresh" content="5">
  <title>Pingnaut</title>
</head>
<body>
<h1>Last 15 results</h1>
<table border="1" cellpadding="5">
<tr><td>timestamp</td><td>source</td><td>destination</td><td>time</td><td>code</td><td></td></tr>
%for i in res:
	<tr><td>{{i[6]}}</td><td>{{i[2]}}</td><td>{{i[4]}}</td><td>{{i[1]}}</td><td>{{i[5]}}</td><td><a href="/tr/{{i[0]}}">route</a></td></tr><p>
%end
</table>
</body>
</html>
