from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ListStyle, ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


TITLE = "Methodology and Technical Design for Learning-Augmented Robust Traffic Engineering"
SUBTITLE = "Detailed Design, Algorithms, Optimization, and Implementation Plan"
COURSE = "ECE GY 7363: Communications Networks II - Design and Algorithms"
DATE = "April 2026"

SECTIONS = [
    (
        "Abstract",
        [
            "This document presents the detailed methodology for the proposed project on learning-augmented robust traffic engineering in software-defined networks. It explains the design formulation, optimization model, machine learning techniques, baseline algorithms, resilience evaluation strategy, implementation architecture, and experimental methodology. The project combines time-series traffic prediction with multi-commodity flow optimization to proactively route traffic in a capacitated network. The primary design goal is to minimize congestion while preserving feasibility and resilience under demand variations and link failures.",
        ],
    ),
    (
        "1. Project Goal",
        [
            "The project studies how to improve traffic engineering decisions in a communication network when traffic demand varies over time and the network may experience failures. The central idea is to combine prediction and optimization in an end-to-end control loop: historical traffic, traffic prediction, routing optimization, and resilience evaluation.",
            "The key hypothesis is that a predictor trained on past traffic matrices can estimate near-future demand well enough to help the controller make better routing decisions than methods that react only to the current state.",
        ],
    ),
    (
        "2. System Model",
        [
            "The network is represented as a directed graph G = (V, E), where V is the set of routers or switches and E is the set of directed links.",
            "Each link (i, j) has capacity c_ij > 0, and the network operates over discrete time epochs.",
            "Each source-destination pair is treated as a commodity k with source s_k, destination t_k, and time-varying demand d_k(t).",
            "The full set of demands at time t forms the traffic matrix, and the ML component predicts one-step-ahead demand values hat(d_k(t+1)).",
        ],
    ),
    (
        "3. Design Formulation",
        [
            "The routing design uses continuous flow variables f_ij^k(t), where each variable denotes the amount of commodity k routed on link (i, j) at time t.",
            "Flow conservation ensures that each source injects its traffic, each destination receives it, and each intermediate node preserves balance.",
            "Capacity constraints ensure the total traffic on each link does not exceed the physical link capacity.",
            "Nonnegativity constraints require all routed flows to be nonnegative.",
            "The primary objective is to minimize the maximum link utilization through an auxiliary variable U(t), leading to a standard min-max congestion traffic engineering model.",
        ],
    ),
    (
        "4. Optimization Techniques",
        [
            "The primary optimization method is linear programming because the routing variables are continuous and all constraints and objectives are linear.",
            "The project uses learning-augmented optimization, where the ML predictor provides the next traffic matrix and the optimizer computes capacity-feasible routes based on that prediction.",
            "The routing loop is implemented as rolling-horizon control: observe traffic, predict the next state, optimize routing, evaluate realized performance, and repeat.",
            "Optional extensions include robust optimization for uncertainty and fairness-aware formulations for equitable flow allocation.",
        ],
    ),
    (
        "5. Algorithms and Techniques",
        [
            "Shortest-path routing with Dijkstra's algorithm serves as the simplest routing baseline.",
            "A current-demand-only LP baseline isolates the value of optimization without prediction.",
            "A conservative non-predictive LP baseline provides a basic robust benchmark.",
            "The prediction layer compares moving average, linear regression, optional MLP, and LSTM as the main forecasting model.",
            "GRU may be considered as an optional lighter recurrent alternative.",
        ],
    ),
    (
        "6. Priority of Advanced ML Models",
        [
            "Priority 1: Transformer-based time-series model. This is the best modern extension because traffic matrices are multivariate time series with long-range temporal dependencies, periodicity, and bursts. It is highly relevant to communication networks and relatively practical to add after LSTM.",
            "Priority 2: Graph Neural Network or Spatio-Temporal GNN. This is highly network-relevant because the system itself is a graph, so a GNN can use topology information directly to model how traffic correlations propagate across connected nodes and links.",
            "Priority 3: Graph Transformer or Spatio-Temporal Graph Transformer. This is the most ambitious option because it combines temporal attention with graph structure learning, but it also has the highest implementation and tuning complexity.",
            "Recommended hierarchy: implement LSTM first, add a Transformer as the main latest-model comparison, then consider a GNN for stronger network structure awareness, and treat the Graph Transformer as a stretch goal.",
        ],
    ),
    (
        "7. Failure Analysis and Resilience Evaluation",
        [
            "Resilience will be tested under random single-link failures, critical-link failures based on utilization or graph centrality, and combined traffic-spike plus failure stress cases.",
            "These scenarios will show whether the learning-augmented optimizer remains effective when the network deviates from nominal conditions.",
        ],
    ),
    (
        "8. Performance Metrics",
        [
            "Maximum link utilization",
            "Average link utilization",
            "Number of overloaded links",
            "Fraction of demand satisfied",
            "Average path length",
            "Jain's fairness index",
            "Performance degradation under failure",
            "Prediction error using MAE, RMSE, and relative error",
        ],
    ),
    (
        "9. End-to-End Algorithm",
        [
            "Load the topology and capacities.",
            "Generate or load time-varying traffic matrices.",
            "Split the traffic sequence into training, validation, and test periods.",
            "Train the traffic prediction model.",
            "For each test step, predict the next traffic matrix, solve the routing LP, evaluate realized performance, and simulate failure scenarios.",
            "Repeat the process for each baseline and compare methods statistically and visually.",
        ],
    ),
    (
        "10. Implementation Architecture",
        [
            "The codebase will be organized into modules for topology handling, traffic generation, predictors, optimization, baselines, failure simulation, metrics, experiments, and plotting.",
            "The software stack will use Python with networkx, numpy, pandas, PyTorch, cvxpy or pulp, matplotlib, and seaborn.",
            "The data flow will go from traffic generation to prediction, from prediction to optimization, and from optimization to evaluation and plotting.",
        ],
    ),
    (
        "11. Experimental Design",
        [
            "Experiments will use standard backbone-style topologies such as NSFNET, Abilene, or GEANT, along with optional synthetic stress-test graphs.",
            "Traffic traces will be generated using base demand, periodic modulation, random noise, bursts, and hotspot pairs to create realistic but reproducible dynamics.",
            "The traffic sequence will be split into training, validation, and test periods, and failure studies will include random and critical-link scenarios.",
        ],
    ),
    (
        "12. Complexity and Practical Considerations",
        [
            "The LP grows with the number of commodities and links, so early experiments will use medium-size networks and may restrict the number of active commodities if necessary.",
            "The LSTM adds training cost but relatively low inference cost, making it practical for repeated control once trained.",
        ],
    ),
    (
        "13. Expected Findings",
        [
            "Optimization-based routing should outperform shortest-path routing under congestion.",
            "Prediction-enhanced routing should outperform current-demand-only routing when traffic contains temporal structure.",
            "Under severe prediction error or extreme failures, conservative baselines may remain competitive.",
            "Resilience analysis will reveal when learning-augmented routing improves or harms robustness.",
        ],
    ),
    (
        "14. Risks and Mitigation",
        [
            "Optimization may become slow on large topologies, so the project will begin with medium-size graphs and scale carefully.",
            "Synthetic traffic may be too noisy for ML to help, so the generator will include controlled temporal structure and forecasting quality will be measured independently.",
            "Full robust optimization may be too ambitious, so scenario-based resilience evaluation is prioritized first.",
        ],
    ),
    (
        "15. Why the Technical Plan is Strong",
        [
            "The methodology combines a rigorous mathematical design formulation, classical optimization, modern ML, systematic baseline comparisons, explicit resilience analysis, and a realistic implementation plan.",
            "That makes the project academically strong and well aligned with the course expectations.",
        ],
    ),
    (
        "16. Conclusion",
        [
            "This methodology document provides the full technical blueprint for carrying the project from idea to implementation and evaluation. The design formulation is a dynamic multi-commodity flow model on a capacitated graph, the main optimization technique is linear programming with a min-max utilization objective, and the main ML technique is LSTM-based traffic prediction.",
        ],
    ),
]


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="PaperTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            alignment=1,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PaperMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#555555"),
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHead",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=10,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PaperBody",
            parent=styles["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=14,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CaptionSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#444444"),
            spaceAfter=6,
        )
    )
    styles.add(
        ListStyle(
            name="BulletList",
            leftIndent=18,
            bulletIndent=6,
        )
    )
    return styles


def short_list(items):
    return len(items) >= 3 and all(len(item) < 140 for item in items)


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawRightString(7.25 * inch, 0.55 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_story(styles):
    story = [
        Spacer(1, 0.2 * inch),
        Paragraph(TITLE, styles["PaperTitle"]),
        Paragraph(SUBTITLE, styles["PaperMeta"]),
        Paragraph(COURSE, styles["PaperMeta"]),
        Paragraph(DATE, styles["PaperMeta"]),
        Spacer(1, 0.15 * inch),
    ]

    summary = Table(
        [
            ["Focus", "Algorithms, design formulation, optimization methods, and implementation plan"],
            ["Core Model", "Dynamic multi-commodity flow routing on a capacitated graph"],
            ["Main Methods", "LSTM traffic prediction, LP routing optimization, resilience testing"],
        ],
        colWidths=[1.5 * inch, 5.0 * inch],
        hAlign="LEFT",
    )
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#D9EAF7")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.8),
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#9BBAD0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([summary, Spacer(1, 0.16 * inch)])

    for heading, items in SECTIONS:
        story.append(Paragraph(heading, styles["SectionHead"]))
        if short_list(items):
            list_items = [ListItem(Paragraph(item, styles["PaperBody"])) for item in items]
            story.append(ListFlowable(list_items, bulletType="bullet", style=styles["BulletList"]))
            story.append(Spacer(1, 0.04 * inch))
        else:
            for item in items:
                story.append(Paragraph(item, styles["PaperBody"]))

    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("Planned Code Modules", styles["SectionHead"]))
    modules = Table(
        [
            ["Module", "Responsibility"],
            ["topology.py", "Load topology, capacities, and graph metadata"],
            ["traffic_generator.py", "Generate synthetic time-varying traffic matrices"],
            ["predictors.py", "Implement moving average, regression, and LSTM models"],
            ["optimizer.py", "Solve LP-based routing problems"],
            ["baselines.py", "Implement shortest-path and non-predictive baselines"],
            ["failure_simulator.py", "Run link-failure scenarios and resilience tests"],
            ["metrics.py", "Compute congestion, fairness, and ML metrics"],
            ["run_experiments.py", "Coordinate the full experiment pipeline"],
            ["plots.py", "Produce comparison figures and summary visuals"],
        ],
        colWidths=[1.8 * inch, 4.7 * inch],
        hAlign="LEFT",
    )
    modules.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AAB7C4")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#F6FAFD")]),
            ]
        )
    )
    story.extend(
        [
            modules,
            Spacer(1, 0.06 * inch),
            Paragraph("Table 1. Proposed implementation modules for the project pipeline.", styles["CaptionSmall"]),
        ]
    )
    return story


def main():
    out = Path(__file__).resolve().parent / "ML_Network_Project_Methodology.pdf"
    styles = make_styles()
    story = build_story(styles)
    doc = SimpleDocTemplate(
        str(out),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=TITLE,
        author=COURSE,
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


if __name__ == "__main__":
    main()
