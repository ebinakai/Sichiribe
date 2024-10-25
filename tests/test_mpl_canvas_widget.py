import pytest
from gui.widgets.mpl_canvas_widget import MplCanvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes


@pytest.fixture
def canvas(qtbot):
    canvas = MplCanvas()
    canvas.show()
    qtbot.addWidget(canvas)
    return canvas


def test_initialization(canvas):
    assert isinstance(canvas.figure, Figure), "Not isinstance of Figure"
    assert isinstance(canvas.axes1, Axes), "Not isinstance of Axes"
    assert isinstance(canvas.axes2, Axes), "Not isinstance of Axes"


def test_gen_graph(canvas):
    canvas.gen_graph(
        "Test Title",
        "X Label",
        "Y1 Label",
        "Y2 Label",
        dark_theme=False)

    assert canvas.axes1.get_title() == "Test Title"
    assert canvas.axes1.xaxis.get_label_text() == "X Label", "X label is not correct"
    assert canvas.axes1.yaxis.get_label_text() == "Y1 Label", "Y1 label is not correct"
    assert canvas.axes2.yaxis.get_label_text() == "Y2 Label", "Y2 label is not correct"


def test_update_existing_plot(canvas):
    canvas.gen_graph(
        "Update Test",
        "Time",
        "Value 1",
        "Value 2",
        dark_theme=False)

    x_val = ["00:00:00", "00:00:01", "00:00:02"]
    y_val1 = [0.1, 0.5, 0.9]
    y_val2 = [0.2, 0.6, 0.8]

    canvas.update_existing_plot(x_val, y_val1, y_val2)

    assert canvas.line1.get_ydata() == pytest.approx(y_val1, rel=1e-2)
    assert canvas.line2.get_ydata() == pytest.approx(y_val2, rel=1e-2)


def test_clear(canvas):
    canvas.gen_graph("Clear Test", "X", "Y1", "Y2", dark_theme=False)

    canvas.clear()

    assert len(canvas.axes1.lines) == 0
    assert len(canvas.axes2.lines) == 0
