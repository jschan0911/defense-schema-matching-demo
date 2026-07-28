import AppKit
import Foundation
import WebKit

final class SnapshotDelegate: NSObject, WKNavigationDelegate {
    let output: URL

    init(output: URL) {
        self.output = output
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            webView.takeSnapshot(with: nil) { image, error in
                guard error == nil,
                      let tiff = image?.tiffRepresentation,
                      let bitmap = NSBitmapImageRep(data: tiff),
                      let png = bitmap.representation(using: .png, properties: [:])
                else {
                    fputs("snapshot failed: \(String(describing: error))\n", stderr)
                    exit(2)
                }
                do {
                    try FileManager.default.createDirectory(
                        at: self.output.deletingLastPathComponent(),
                        withIntermediateDirectories: true
                    )
                    try png.write(to: self.output)
                    print(self.output.path)
                    exit(0)
                } catch {
                    fputs("write failed: \(error)\n", stderr)
                    exit(3)
                }
            }
        }
    }
}

guard CommandLine.arguments.count == 3,
      let pageURL = URL(string: CommandLine.arguments[1])
else {
    fputs("usage: render_ui.swift URL OUTPUT.png\n", stderr)
    exit(1)
}

let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let app = NSApplication.shared
let configuration = WKWebViewConfiguration()
let webView = WKWebView(
    frame: NSRect(x: 0, y: 0, width: 1440, height: 1000),
    configuration: configuration
)
let delegate = SnapshotDelegate(output: outputURL)
webView.navigationDelegate = delegate
webView.load(URLRequest(url: pageURL))
DispatchQueue.main.asyncAfter(deadline: .now() + 15) {
    fputs("snapshot timed out\n", stderr)
    exit(4)
}
app.run()

