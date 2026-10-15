param(
    [string]$LayoutPath = '.review-qa/powerpoint_layout.json',
    [string]$OutputPath = 'review/green_tac_prototype_review.pptx',
    [string]$PreviewPath = '.review-qa/powerpoint-render'
)
$ErrorActionPreference = 'Stop'
function ColorValue([string]$CssColor) {
    $numbers = [regex]::Matches($CssColor, '\d+')
    return [int]$numbers[0].Value + 256 * [int]$numbers[1].Value + 65536 * [int]$numbers[2].Value
}
$rootPath = (Get-Location).Path
$slideData = Get-Content -LiteralPath (Join-Path $rootPath $LayoutPath) -Raw -Encoding UTF8 | ConvertFrom-Json
$finalPath = Join-Path $rootPath $OutputPath
$renderPath = Join-Path $rootPath $PreviewPath
if (Test-Path -LiteralPath $finalPath) { throw 'Output already exists; choose another filename.' }
New-Item -ItemType Directory -Force -Path $renderPath | Out-Null
$app = $null
$presentation = $null
$existingCount = -1
try {
    $app = New-Object -ComObject PowerPoint.Application
    $existingCount = $app.Presentations.Count
    $app.DisplayAlerts = 1
    $presentation = $app.Presentations.Add(0)
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540
    $index = 0
    foreach ($entry in $slideData) {
        $index++
        $slide = $presentation.Slides.Add($index, 12)
        $slide.FollowMasterBackground = 0
        $slide.Background.Fill.Solid()
        $slide.Background.Fill.ForeColor.RGB = ColorValue $entry.background
        foreach ($item in $entry.items) {
            $left = [single]($item.x * 0.75)
            $top = [single]($item.y * 0.75)
            $width = [single]($item.w * 0.75)
            $height = [single]($item.h * 0.75)
            if ($item.type -eq 'table') {
                $shape = $slide.Shapes.AddTable($item.rows.Count, $item.widths.Count, $left, $top, $width, $height)
                $table = $shape.Table
                for ($c = 1; $c -le $item.widths.Count; $c++) {
                    $table.Columns.Item($c).Width = [single]($item.widths[$c-1] * 0.75)
                }
                for ($r = 1; $r -le $item.rows.Count; $r++) {
                    $row = $item.rows[$r-1]
                    for ($c = 1; $c -le $row.cells.Count; $c++) {
                        $cellData = $row.cells[$c-1]
                        $cell = $table.Cell($r, $c)
                        $cell.Shape.Fill.Solid()
                        $cell.Shape.Fill.ForeColor.RGB = ColorValue $entry.background
                        $tf = $cell.Shape.TextFrame
                        $tf.MarginLeft = 9
                        $tf.MarginRight = 9
                        $tf.MarginTop = 10
                        $tf.MarginBottom = 10
                        $tf.VerticalAnchor = 3
                        $tf.TextRange.Text = $cellData.text
                        $tf.TextRange.Font.Name = $cellData.font
                        $tf.TextRange.Font.Size = [single]($cellData.size * 0.75)
                        $tf.TextRange.Font.Color.RGB = ColorValue $cellData.color
                        $tf.TextRange.Font.Bold = $(if ($cellData.bold) {-1} else {0})
                        $tf.TextRange.ParagraphFormat.SpaceBefore = 0
                        $tf.TextRange.ParagraphFormat.SpaceAfter = 0
                        foreach ($borderIndex in 1..4) {
                            $cell.Borders.Item($borderIndex).Visible = 0
                        }
                        $cell.Borders.Item(3).Visible = -1
                        $cell.Borders.Item(3).ForeColor.RGB = $(if ($r -eq 1) {ColorValue 'rgb(55,106,77)'} else {ColorValue 'rgb(201,212,201)'})
                        $cell.Borders.Item(3).Weight = $(if ($r -eq 1) {1.5} else {0.75})
                    }
                    $table.Rows.Item($r).Height = [single]($row.h * 0.75)
                }
            } else {
                if ([string]::IsNullOrWhiteSpace($item.text)) { continue }
                $shape = $slide.Shapes.AddTextbox(1, $left, $top, $width, $height)
                $shape.Name = 'Text ' + $slide.Shapes.Count
                $shape.Fill.Visible = 0
                $shape.Line.Visible = 0
                $tf = $shape.TextFrame
                $tf.MarginLeft = 0
                $tf.MarginRight = 0
                $tf.MarginTop = 0
                $tf.MarginBottom = 0
                $tf.AutoSize = 0
                $tf.WordWrap = -1
                $text = $item.text
                if ($entry.title -eq 'Carbon objective and proposed contribution' -and $text.StartsWith('C =')) {
                    $text = 'C = (E_compile CI_compile + N E_runtime CI_runtime) / 3,600,000'
                }
                $tf.TextRange.Text = $text
                $tf.TextRange.Font.Name = $item.font
                $tf.TextRange.Font.Size = [single]($item.size * 0.75)
                $tf.TextRange.Font.Color.RGB = ColorValue $item.color
                $tf.TextRange.Font.Bold = $(if ($item.bold) {-1} else {0})
                $tf.TextRange.ParagraphFormat.SpaceBefore = 0
                $tf.TextRange.ParagraphFormat.SpaceAfter = 0
                $tf.TextRange.ParagraphFormat.LineRuleWithin = 0
                $tf.TextRange.ParagraphFormat.SpaceWithin = [single]($item.lineHeight * 0.75)
                $shape.Height = [single][Math]::Max($height, $tf.TextRange.BoundHeight + 2)
            }
        }
        $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $entry.notes
    }
    $presentation.SaveAs($finalPath, 24)
    $presentation.Export($renderPath, 'PNG', 1280, 720)
    $checks = @()
    foreach ($slide in $presentation.Slides) {
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $checks += [pscustomobject]@{
                    Slide = $slide.SlideIndex
                    Text = $shape.TextFrame.TextRange.Text
                    Width = $shape.Width
                    Height = $shape.Height
                    TextWidth = $shape.TextFrame.TextRange.BoundWidth
                    TextHeight = $shape.TextFrame.TextRange.BoundHeight
                }
            }
        }
    }
    $checks | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $renderPath 'text_fit.json')
    Write-Output "Created $($presentation.Slides.Count) editable PowerPoint slides at $finalPath"
} finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($null -ne $app -and $existingCount -eq 0) { $app.Quit() }
}
