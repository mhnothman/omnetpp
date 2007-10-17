package com.simulcraft.test.gui.recorder.object;

import org.eclipse.swt.widgets.Shell;

import com.simulcraft.test.gui.recorder.GUIRecorder;
import com.simulcraft.test.gui.recorder.JavaSequence;

public class ShellRecognizer extends ObjectRecognizer {
    public ShellRecognizer(GUIRecorder recorder) {
        super(recorder);
    }

    public JavaSequence identifyObject(Object uiObject) {
        if (uiObject instanceof Shell) {
            Shell shell = (Shell)uiObject;
            return wrap("findShellWithTitle(" + quote(shell.getText()) + ")", 0.5);
        }
        return null;
    }
}