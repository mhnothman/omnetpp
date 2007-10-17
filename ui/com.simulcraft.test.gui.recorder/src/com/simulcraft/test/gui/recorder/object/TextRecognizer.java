package com.simulcraft.test.gui.recorder.object;

import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

import com.simulcraft.test.gui.recorder.GUIRecorder;
import com.simulcraft.test.gui.recorder.JavaSequence;

public class TextRecognizer extends ObjectRecognizer {
    public TextRecognizer(GUIRecorder recorder) {
        super(recorder);
    }

    public JavaSequence identifyObject(Object uiObject) {
        if (uiObject instanceof Text) {
            Text text = (Text)uiObject;
            Label label = getPrecedingUniqueLabel(text.getShell(), text);
            if (label != null)
                return chainO(text.getShell(), "findTextAfterLabel("+quote(label.getText()) + ")", 0.8);
        }
        return null;
    }
}